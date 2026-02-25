-- Enable pgcrypto extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encryption functions with key parameter
CREATE OR REPLACE FUNCTION encrypt_token(plaintext TEXT, key_text TEXT)
RETURNS BYTEA AS $$
BEGIN
    IF plaintext IS NULL THEN
        RETURN NULL;
    END IF;
    RETURN pgp_sym_encrypt(plaintext, key_text);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION decrypt_token(encrypted BYTEA, key_text TEXT)
RETURNS TEXT AS $$
BEGIN
    IF encrypted IS NULL THEN
        RETURN NULL;
    END IF;
    RETURN pgp_sym_decrypt(encrypted, key_text);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Log initialization
SELECT 'pgcrypto extension and encryption functions created' AS status;
