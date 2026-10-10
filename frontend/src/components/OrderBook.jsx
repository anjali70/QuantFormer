
export default function OrderBook({ orderBook }) {
  if (!orderBook) {
    return (
      <section className="panel">
        <h2>Depth of Market</h2>
        <p className="muted">Waiting for order book...</p>
      </section>
    );
  }

  return (
    <section className="panel">
      <h2>Depth of Market</h2>

      <div className="dom-header">
        <span>Price</span>
        <span>Volume</span>
      </div>

      <div className="asks">
        {[...orderBook.asks].reverse().map((level, index) => (
          <div className="dom-row ask" key={`ask-${index}`}>
            <span>{Number(level.price).toFixed(2)}</span>
            <span>{level.volume}</span>
          </div>
        ))}
      </div>

      <div className="mid-price">
        <span>Mid Price</span>
        <strong>{Number(orderBook.mid_price).toFixed(2)}</strong>
      </div>

      <div className="bids">
        {orderBook.bids.map((level, index) => (
          <div className="dom-row bid" key={`bid-${index}`}>
            <span>{Number(level.price).toFixed(2)}</span>
            <span>{level.volume}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
