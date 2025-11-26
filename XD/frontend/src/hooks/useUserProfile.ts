import { useQuery } from '@tanstack/react-query';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const useUserProfile = (userId?: string | number) => {
  return useQuery({
    queryKey: ['userProfile', userId],
    queryFn: async () => {
      if (!userId) return null;

      try {
        // Fetch real user data from backend
        const response = await fetch(`${API_BASE_URL}/auth/user/${userId}`);

        if (!response.ok) {
          throw new Error('Failed to fetch user profile');
        }

        const data = await response.json();

        if (data.success && data.user) {
          return {
            user_id: data.user.id,
            full_name: data.user.full_name || data.user.username,
            email: data.user.email,
            username: data.user.username,
            is_active: data.user.is_active,
            created_at: data.user.created_at,
            // Real data from database
            province: data.user.province || 'กรุงเทพมหานคร',
            water_availability: data.user.water_availability || 'ปานกลาง',
            budget_level: data.user.budget_level || 'ปานกลาง',
            experience_crops: data.user.experience_crops || ['ข้าว', 'ข้าวโพด'],
            risk_tolerance: data.user.risk_tolerance || 'ปานกลาง',
            time_constraint: data.user.time_constraint || 6,
            preference: data.user.preference || 'ผลผลิตสูง',
            soil_type: data.user.soil_type || 'ดินร่วน'
          };
        }

        return null;
      } catch (error) {
        console.error('Error fetching user profile:', error);
        return null;
      }
    },
    enabled: !!userId,
    staleTime: 5 * 60 * 1000, // Data stays fresh for 5 minutes
    gcTime: 10 * 60 * 1000, // Cache for 10 minutes (formerly cacheTime)
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
    refetchOnMount: false, // Don't refetch on component mount if data exists
    refetchInterval: false, // Don't auto-refetch
  });
};
