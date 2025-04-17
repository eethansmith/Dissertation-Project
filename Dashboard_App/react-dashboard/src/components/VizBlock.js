import React, { useEffect, useRef } from 'react';

const VizBlock = ({ id, children, renderViz }) => {
  const containerRef = useRef(null);

  useEffect(() => {
    if (renderViz && containerRef.current) {
      renderViz(containerRef.current);
    }
  }, [renderViz]);

  return (
    <div
      className="data-viz-block"
      id={id}
      ref={containerRef}
      style={{ minHeight: '400px', width: '100%', border: '1px solid #ccc' }}
    >
      {/* Render children normally */}
      {children}
    </div>
  );
};

export default VizBlock;
