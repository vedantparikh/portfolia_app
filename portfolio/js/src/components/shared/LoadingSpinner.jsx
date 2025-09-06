import React from 'react';

const LoadingSpinner = ({
    size = 'md',
    color = 'primary',
    text = '',
    className = '',
    centered = false
}) => {
    const getSizeClasses = () => {
        switch (size) {
            case 'sm':
                return 'h-4 w-4';
            case 'md':
                return 'h-8 w-8';
            case 'lg':
                return 'h-12 w-12';
            case 'xl':
                return 'h-16 w-16';
            default:
                return 'h-8 w-8';
        }
    };

    const getColorClasses = () => {
        switch (color) {
            case 'primary':
                return 'border-primary-500';
            case 'white':
                return 'border-white';
            case 'gray':
                return 'border-gray-400';
            case 'success':
                return 'border-green-500';
            case 'danger':
                return 'border-red-500';
            default:
                return 'border-primary-500';
        }
    };

    const getTextColorClasses = () => {
        switch (color) {
            case 'primary':
                return 'text-primary-400';
            case 'white':
                return 'text-white';
            case 'gray':
                return 'text-gray-400';
            case 'success':
                return 'text-green-400';
            case 'danger':
                return 'text-red-400';
            default:
                return 'text-gray-400';
        }
    };

    const spinner = (
        <div className={`animate-spin rounded-full border-b-2 ${getSizeClasses()} ${getColorClasses()} ${className}`} />
    );

    if (centered) {
        return (
            <div className="flex items-center justify-center">
                <div className="text-center">
                    {spinner}
                    {text && (
                        <p className={`mt-2 text-sm ${getTextColorClasses()}`}>
                            {text}
                        </p>
                    )}
                </div>
            </div>
        );
    }

    if (text) {
        return (
            <div className="flex items-center space-x-2">
                {spinner}
                <span className={`text-sm ${getTextColorClasses()}`}>
                    {text}
                </span>
            </div>
        );
    }

    return spinner;
};

export default LoadingSpinner;
