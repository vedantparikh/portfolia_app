const Sparkline = ({ values, width = 80, height = 24, className = 'text-primary-400', title }) => {
    if (!values || values.length < 2) return null;
    const min = Math.min(...values);
    const range = Math.max(...values) - min || 1;
    const step = width / (values.length - 1);
    const points = values
        .map((v, i) => `${(i * step).toFixed(1)},${(height - 1 - ((v - min) / range) * (height - 2)).toFixed(1)}`)
        .join(' ');

    return (
        <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} className={`block ${className}`} role="img" aria-label={title}>
            {title && <title>{title}</title>}
            <polyline points={points} fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" strokeLinecap="round" />
        </svg>
    );
};

export default Sparkline;
