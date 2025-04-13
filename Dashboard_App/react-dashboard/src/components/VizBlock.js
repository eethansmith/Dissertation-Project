// VizBlock.js
import React, { useEffect, useRef } from 'react';

const VizBlock = ({ id, renderViz }) => {
  const containerRef = useRef(null);

// Modify the useEffect in VizBlock.jsx if necessary
useEffect(() => {
    const handleResize = () => {
      if (containerRef.current && renderViz) {
        renderViz(containerRef.current);
      }
    };
  
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [renderViz]);
  
  return (
    <div className="data-viz-block" id={id} ref={containerRef}>
      {/* Your interactive visualization will render here */}
    </div>
  );
};

export default VizBlock;
