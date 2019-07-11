CREATE TABLE taurus.candlesticks (
    id int NOT NULL AUTO_INCREMENT,
    time int,
    open double,
    high double,
    low double,
    close double,
    volume double,
    symbol varchar(10),
    primary key (id)
);

CREATE TABLE taurus.trades (
    id int NOT NULL AUTO_INCREMENT,
    info text,
    trade_id text,
    time int,
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
);