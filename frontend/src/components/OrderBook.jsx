
export default function OrderBook({ orderBook }) {
  if (!orderBook) {
    return (
      <section className="surface-card orderbook-card">
        <div className="card-heading">
          <div>
            <h3>Market Depth</h3>
            <p>Live liquidity distribution</p>
          </div>
          <span className="subtle-tag">WAITING</span>
        </div>

        <div className="empty-state">
          <span className="empty-icon">◈</span>
          <p>Waiting for market liquidity...</p>
        </div>
      </section>
    );
  }

  const asks = [...(orderBook.asks || [])].reverse();
  const bids = orderBook.bids || [];

  const maxVolume = Math.max(
    1,
    ...asks.map((x) => Number(x.volume) || 0),
    ...bids.map((x) => Number(x.volume) || 0)
  );

  const bestAsk = asks.length
    ? Number(asks[asks.length - 1].price)
    : null;

  const bestBid = bids.length
    ? Number(bids[0].price)
    : null;

  const spread =
    bestAsk !== null && bestBid !== null
      ? bestAsk - bestBid
      : null;

  const renderLevel = (level, index, type) => {
    const volume = Number(level.volume) || 0;
    const price = Number(level.price);
    const width = (volume / maxVolume) * 100;

    return (
      <div className={`dom-row ${type}`} key={`${type}-${index}`}>
        <span className="dom-price">
          {Number.isFinite(price) ? price.toFixed(2) : "—"}
        </span>

        <div className="dom-volume-cell">
          <div
            className={`dom-volume-bar ${type}-bar`}
            style={{ width: `${width}%` }}
          />

          <span>{volume.toLocaleString()}</span>
        </div>
      </div>
    );
  };

  return (
    <section className="surface-card orderbook-card">

      <div className="card-heading">
        <div>
          <h3>Market Depth</h3>
          <p>Live bid and ask liquidity</p>
        </div>

        <span className="live-indicator">
          <span className="status-dot online" />
          LIVE
        </span>
      </div>

      <div className="orderbook-summary">
        <div>
          <span>BEST BID</span>
          <strong className="bid-text">
            {bestBid === null ? "—" : bestBid.toFixed(2)}
          </strong>
        </div>

        <div>
          <span>BEST ASK</span>
          <strong className="ask-text">
            {bestAsk === null ? "—" : bestAsk.toFixed(2)}
          </strong>
        </div>
      </div>

      <div className="dom-columns">
        <span>PRICE</span>
        <span>VOLUME</span>
      </div>

      <div className="asks">
        <div className="dom-side-label ask-label">
          SELL ORDERS
        </div>

        {asks.map((level, index) =>
          renderLevel(level, index, "ask")
        )}
      </div>

      <div className="dom-mid-price">
        <div>
          <span>MARKET MID PRICE</span>
          <strong>
            {Number(orderBook.mid_price).toFixed(2)}
          </strong>
        </div>

        <div className="dom-spread">
          <span>SPREAD</span>
          <strong>
            {spread === null ? "—" : spread.toFixed(4)}
          </strong>
        </div>
      </div>

      <div className="bids">
        <div className="dom-side-label bid-label">
          BUY ORDERS
        </div>

        {bids.map((level, index) =>
          renderLevel(level, index, "bid")
        )}
      </div>

      <div className="dom-legend">
        <span><i className="legend-ask" /> Ask liquidity</span>
        <span><i className="legend-bid" /> Bid liquidity</span>
      </div>

    </section>
  );
}
