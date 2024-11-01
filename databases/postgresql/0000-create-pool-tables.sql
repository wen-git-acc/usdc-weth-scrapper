-- +migrate Up
CREATE TABLE token_pair_pools (
    pool_id SERIAL PRIMARY KEY,
    pool_name VARCHAR(255)  UNIQUE NOT NULL,
    contract_address VARCHAR(42) UNIQUE NOT NULL
);

CREATE TABLE transactions_to_from_pools (
    transaction_id SERIAL PRIMARY KEY,
    block_number BIGINT NOT NULL,
    ts_timestamp BIGINT NOT NULL,
    tx_hash VARCHAR(66) UNIQUE NOT NULL,         -- 66 characters for tx hashes with '0x' prefix
    from_address VARCHAR(42) NOT NULL,
    to_address VARCHAR(42) NOT NULL,
    contract_address VARCHAR(42) NOT NULL,
    token_value VARCHAR(255) NOT NULL,               -- 38 digits for high precision token values
    token_name VARCHAR(50),
    token_symbol VARCHAR(20),
    token_decimal VARCHAR(255),
    transaction_index VARCHAR(255) NOT NULL,
    gas_limit VARCHAR(255) NOT NULL,                   -- Original gas limit provided by the sender
    gas_price VARCHAR(255) NOT NULL,                   -- Gas price in wei
    gas_used VARCHAR(255) NOT NULL,                             -- Actual gas used
    cumulative_gas_used VARCHAR(255),
    confirmations VARCHAR(255),
    transaction_fee_usdt VARCHAR(255),
    pool_id INTEGER REFERENCES token_pair_pools(pool_id) ON DELETE SET NULL
);

CREATE INDEX idx_tx_hash ON transactions_to_from_pools(tx_hash);
CREATE INDEX idx_from_address ON transactions_to_from_pools(from_address);
CREATE INDEX idx_to_address ON transactions_to_from_pools(to_address);

-- +migrate Down
DROP TABLE IF EXISTS transactions_to_from_pools;
DROP TABLE IF EXISTS token_pair_pools;