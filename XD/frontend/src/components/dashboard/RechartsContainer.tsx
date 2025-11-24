import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';

interface RechartsContainerProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  actions?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

const RechartsContainer: React.FC<RechartsContainerProps> = ({
  title,
  description,
  icon,
  actions,
  children,
  className = '',
}) => {
  return (
    <Card className={`bg-white shadow-md hover:shadow-lg transition-shadow duration-300 ${className}`}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {icon && <div className="text-emerald-600">{icon}</div>}
            <CardTitle className="text-lg font-semibold text-gray-900">{title}</CardTitle>
          </div>
          {actions && <div>{actions}</div>}
        </div>
        {description && (
          <CardDescription className="text-sm text-gray-500 mt-1">
            {description}
          </CardDescription>
        )}
      </CardHeader>
      <CardContent className="pt-0">
        {children}
      </CardContent>
    </Card>
  );
};

export default RechartsContainer;
