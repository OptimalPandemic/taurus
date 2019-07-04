CREATE TABLE candlesticks (
    id int,
    time TIMESTAMP,
    open double,
    high double,
    low double,
    close double,
    volume double,
    symbol varchar(10),
    primary key (id)
);

CREATE TABLE trades (
    id int,
    info text,
    trade_id text,
    time timestamp,
    date_time datetime,
    symbol varchar(10),
    order_id text,
    type varchar(10),
    side varchar(10),
    takerOrMaker varchar(10),
    price double,
    amount double,
    cost double,
    fee_cost double,
    fee_currency varchar(10),
    fee_rate double
)