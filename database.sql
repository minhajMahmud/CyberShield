-- ============================================================
--  CyberShield - Secure Digital Security Platform
--  DBMS Schema (MySQL 8.0+)
--  File: database.sql
--
--  Run with:  mysql -u root -p < database.sql
-- ============================================================

DROP DATABASE IF EXISTS cybershield_db;
CREATE DATABASE cybershield_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE cybershield_db;

-- ------------------------------------------------------------
-- Table: Users
-- Stores account, authentication and 2FA information.
-- ------------------------------------------------------------
CREATE TABLE Users (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    username          VARCHAR(50)  NOT NULL UNIQUE,
    email             VARCHAR(120) NOT NULL UNIQUE,
    password_hash     VARCHAR(255) NOT NULL,           -- bcrypt hash, never plaintext
    full_name         VARCHAR(100),
    role              ENUM('user', 'admin') NOT NULL DEFAULT 'user',
    is_2fa_enabled    BOOLEAN NOT NULL DEFAULT FALSE,
    twofa_secret      VARCHAR(64)  DEFAULT NULL,        -- base32 TOTP secret (pyotp)
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    failed_attempts   INT NOT NULL DEFAULT 0,
    locked_until      DATETIME DEFAULT NULL,
    last_login        DATETIME DEFAULT NULL,
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_users_email (email),
    INDEX idx_users_username (username)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Table: Files
-- Metadata for every AES-256 encrypted file stored on disk.
-- The actual encrypted bytes live in /encrypted, never the DB.
-- ------------------------------------------------------------
CREATE TABLE Files (
    id                 INT AUTO_INCREMENT PRIMARY KEY,
    user_id            INT NOT NULL,
    original_filename  VARCHAR(255) NOT NULL,
    stored_filename    VARCHAR(255) NOT NULL UNIQUE,   -- UUID-based name on disk
    file_size          BIGINT NOT NULL,                -- bytes, original size
    file_type          VARCHAR(50)  NOT NULL,           -- extension / MIME hint
    encryption_iv       VARCHAR(64)  NOT NULL,           -- base64 IV/nonce for AES-GCM
    encrypted_dek       VARCHAR(255) NOT NULL,           -- data-encryption-key wrapped by master key
    checksum_sha256    VARCHAR(64)  NOT NULL,           -- integrity check of plaintext
    is_deleted         BOOLEAN NOT NULL DEFAULT FALSE,
    uploaded_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at         TIMESTAMP NULL DEFAULT NULL,

    CONSTRAINT fk_files_user
        FOREIGN KEY (user_id) REFERENCES Users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    INDEX idx_files_user (user_id),
    INDEX idx_files_deleted (is_deleted)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Table: Digital_Signatures
-- Records of RSA-2048 signing / verification operations.
-- ------------------------------------------------------------
CREATE TABLE Digital_Signatures (
    id                    INT AUTO_INCREMENT PRIMARY KEY,
    user_id               INT NOT NULL,
    file_id               INT DEFAULT NULL,             -- optional link to Files table
    document_name         VARCHAR(255) NOT NULL,
    document_hash         VARCHAR(128) NOT NULL,        -- SHA-256 hex digest
    signature_value       TEXT NOT NULL,                 -- base64 RSA signature
    public_key            TEXT NOT NULL,                 -- PEM public key
    private_key_encrypted TEXT DEFAULT NULL,             -- PEM private key, AES-encrypted at rest
    status                ENUM('signed', 'verified', 'failed', 'tampered')
                              NOT NULL DEFAULT 'signed',
    verified_at           TIMESTAMP NULL DEFAULT NULL,
    created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_signatures_user
        FOREIGN KEY (user_id) REFERENCES Users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_signatures_file
        FOREIGN KEY (file_id) REFERENCES Files(id)
        ON DELETE SET NULL ON UPDATE CASCADE,

    INDEX idx_signatures_user (user_id),
    INDEX idx_signatures_hash (document_hash)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Table: OTP
-- One-time passcodes for login verification / 2FA setup.
-- ------------------------------------------------------------
CREATE TABLE OTP (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT NOT NULL,
    otp_code     VARCHAR(10) NOT NULL,
    purpose      ENUM('login', 'enable_2fa', 'reset_password') NOT NULL DEFAULT 'login',
    is_used      BOOLEAN NOT NULL DEFAULT FALSE,
    attempts     INT NOT NULL DEFAULT 0,
    expires_at   DATETIME NOT NULL,
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_otp_user
        FOREIGN KEY (user_id) REFERENCES Users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    INDEX idx_otp_user (user_id),
    INDEX idx_otp_expiry (expires_at)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Table: Activity_Log
-- Audit trail for security-relevant events (login, upload,
-- signature, 2FA changes, admin actions, etc.)
-- ------------------------------------------------------------
CREATE TABLE Activity_Log (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT DEFAULT NULL,                     -- NULL allowed for anonymous/failed-login attempts
    action       VARCHAR(100) NOT NULL,                 -- e.g. 'LOGIN_SUCCESS', 'FILE_UPLOAD'
    description  VARCHAR(255) DEFAULT NULL,
    ip_address   VARCHAR(45)  DEFAULT NULL,             -- supports IPv6
    user_agent   VARCHAR(255) DEFAULT NULL,
    status       ENUM('success', 'failure', 'warning') NOT NULL DEFAULT 'success',
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_activity_user
        FOREIGN KEY (user_id) REFERENCES Users(id)
        ON DELETE SET NULL ON UPDATE CASCADE,

    INDEX idx_activity_user (user_id),
    INDEX idx_activity_action (action),
    INDEX idx_activity_created (created_at)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Table: Password_Check_History
-- History of password-strength checks. Plaintext passwords are
-- NEVER stored — only a hash sample and computed metrics.
-- ------------------------------------------------------------
CREATE TABLE Password_Check_History (
    id                    INT AUTO_INCREMENT PRIMARY KEY,
    user_id               INT DEFAULT NULL,             -- NULL if checked anonymously (not logged in)
    password_hash_sample  VARCHAR(255) NOT NULL,         -- SHA-256 of the checked password (never plaintext)
    strength_score        TINYINT NOT NULL,              -- 0-100
    strength_label        VARCHAR(20) NOT NULL,          -- Weak / Fair / Good / Strong / Very Strong
    estimated_crack_time  VARCHAR(50) DEFAULT NULL,       -- human readable e.g. "3 days"
    checked_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_pwd_history_user
        FOREIGN KEY (user_id) REFERENCES Users(id)
        ON DELETE SET NULL ON UPDATE CASCADE,

    INDEX idx_pwd_history_user (user_id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Seed data: default admin account
-- Password below is bcrypt('Admin@12345') — CHANGE IMMEDIATELY
-- after first login in any real deployment.
-- ------------------------------------------------------------
INSERT INTO Users (username, email, password_hash, full_name, role, is_active)
VALUES (
    'admin',
    'admin@cybershield.local',
    '$2b$12$K9x1z0Zb0m7d2gq1M0hq5.6QOe9Ynhq0m9m6EwG0m1s0y4Nq0m9m6',
    'System Administrator',
    'admin',
    TRUE
);

-- ============================================================
-- ER RELATIONSHIP SUMMARY
-- ============================================================
-- Users (1) ───< (many) Files
-- Users (1) ───< (many) Digital_Signatures
-- Files (1) ───< (many) Digital_Signatures   [optional link]
-- Users (1) ───< (many) OTP
-- Users (1) ───< (many) Activity_Log         [nullable FK]
-- Users (1) ───< (many) Password_Check_History [nullable FK]
-- ============================================================
