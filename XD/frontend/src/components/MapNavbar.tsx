import React from 'react';
import { Button } from '@/components/ui/button';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { LogOut, User, Settings, ChevronDown } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

const MapNavbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, signOut } = useAuth();

  return (
    <nav className="bg-white pt-0.5 sticky top-0 z-50 mx-auto">
    <div className="container max-w-7xl w-[90%] mx-auto px-6 py-4 mt-10 shadow-sm flex items-center justify-between h-[90px]  rounded-full">
      {/* Logo */}
      <div className="flex-1">
        <img 
          src="/Farmme_ml/XD/frontend/dist/logo.png" 
          alt="FarmTime Logo" 
          className="h-16 w-auto"
        />
      </div>
      
      {/* Navigation Links - Centered */}
      <div className="hidden md:flex flex-1 justify-center">
        <div className="flex items-center space-x-8">
          <Button 
            variant="ghost" 
            className={`font-medium ${(location.pathname === '/' || location.pathname === '/map') ? 'text-emerald-600' : 'text-gray-500 hover:text-emerald-600'}`}
            onClick={() => navigate('/')}
          >
            Home
          </Button>
          <Button 
            variant="ghost" 
            className={`font-medium ${location.pathname === '/overview' ? 'text-emerald-600' : 'text-gray-500 hover:text-emerald-600'}`}
            onClick={() => navigate('/overview')}
          >
            Overview
          </Button>
          <Button 
            variant="ghost" 
            className={`font-medium ${location.pathname === '/forecast' ? 'text-emerald-600' : 'text-gray-500 hover:text-emerald-600'}`}
            onClick={() => navigate('/forecast')}
          >
            Forecast
          </Button>
          <Button 
            variant="ghost" 
            className={`font-medium ${location.pathname === '/chatai' ? 'text-emerald-600' : 'text-gray-500 hover:text-emerald-600'}`}
            onClick={() => navigate('/chatai')}
          >
            Chat AI
          </Button>
          {/* <Button 
            variant="ghost" 
            className={`font-medium ${location.pathname === '/planting-schedule' ? 'text-emerald-600' : 'text-gray-500 hover:text-emerald-600'}`}
            onClick={() => navigate('/planting-schedule')}
          >
            วางแผนปลูก
          </Button> */}
        </div>
      </div>
      
      {/* Auth Buttons */}
      <div className="flex-1 flex justify-end">
        <div className="flex items-center space-x-4">
          {user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button 
                  variant="ghost" 
                  className="flex items-center gap-2 text-gray-700 hover:text-emerald-600"
                >
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center">
                      <User className="w-4 h-4 text-emerald-600" />
                    </div>
                    <span className="text-sm font-medium">{user.email}</span>
                  </div>
                  <ChevronDown className="w-4 h-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>บัญชีของฉัน</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem 
                  onClick={() => navigate('/profile')}
                  className="cursor-pointer"
                >
                  <Settings className="w-4 h-4 mr-2" />
                  <span>แก้ไขข้อมูลส่วนตัว</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem 
                  onClick={signOut}
                  className="cursor-pointer text-red-600 focus:text-red-600"
                >
                  <LogOut className="w-4 h-4 mr-2" />
                  <span>ออกจากระบบ</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Button 
              onClick={() => navigate('/auth')}
              className="bg-emerald-600 hover:bg-emerald-700 text-white font-medium flex items-center gap-2"
            >
              <User className="w-4 h-4" />
              เข้าสู่ระบบ
            </Button>
          )}
        </div>
      </div>
    </div>
  </nav>
  );
};

export default MapNavbar;