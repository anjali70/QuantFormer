export default function OrderBook({ orderBook }) {

  if (!orderBook) {
    return (
      <div className="panel">
        Waiting for order book...
      </div>
    );
  }

  return (
    <div className="panel">

      <h2>Depth of Market</h2>

      <div className="dom-header">
        <span>Price</span>
        <span>Volume</span>
      </div>

      <div className="asks">

        {[...orderBook.asks]
          .reverse()
          .map((level, index) => (

            <div className="dom-row ask" key={index}>

              <span>
                {level.price.toFixed(2)}
              </span>

              <span>
                {level.volume}
              </span>

            </div>

          ))}

      </div>

      <div className="mid-price">

        MID

        <strong>
          {orderBook.mid_price.toFixed(2)}
        </strong>

      </div>

      <div className="bids">

        {orderBook.bids.map((level, index) => (

          <div className="dom-row bid" key={index}>

            <span>
              {level.price.toFixed(2)}
            </span>

            <span>
              {level.volume}
            </span>

          </div>

        ))}

      </div>

    </div>
  );
}