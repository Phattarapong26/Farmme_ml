import React from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ChartContainerProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  isLoading?: boolean;
  error?: string;
  footer?: React.ReactNode;
  className?: string;
  icon?: React.ReactNode;
}

const ChartContainer: React.FC<ChartContainerProps> = ({
  title,
  description,
  children,
  isLoading,
  error,
  footer,
  className,
  icon
}) => {
  return (
    <Card className={cn('hover:shadow-lg transition-shadow duration-300', className)}>
      <CardHeader className="border-b">
        <div className="flex items-center gap-2">
          {icon}
          <div className="flex-1">
            <CardTitle className="text-lg">{title}</CardTitle>
            {description && <CardDescription>{description}</CardDescription>}
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-6 min-h-[400px]">
        {isLoading ? (
          <div className="space-y-3">
            <Skeleton className="h-80 w-full" />
            <div className="flex gap-2">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-4 w-20" />
            </div>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center h-80 text-center">
            <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
            <p className="text-red-600 font-medium mb-2">เกิดข้อผิดพลาด</p>
            <p className="text-gray-500 text-sm">{error}</p>
          </div>
        ) : (
          <div className="w-full h-full">
            {children}
          </div>
        )}
      </CardContent>
      {footer && (
        <CardFooter className="bg-gray-50 text-sm text-gray-600 border-t">
          {footer}
        </CardFooter>
      )}
    </Card>
  );
};

export default ChartContainer;
