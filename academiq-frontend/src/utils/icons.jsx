// Icon component to replace emojis throughout the app
// Using Lucide React icons (already included in most React projects)

import {
  BarChart3,
  TrendingUp,
  AlertTriangle,
  Target,
  AlertCircle,
  Upload,
  Building2,
  GraduationCap,
  File,
  Mail,
  LogOut,
  Users,
  Check,
  X,
  Heart,
  Search,
  Menu,
  DollarSign,
  Settings,
  Eye,
} from 'lucide-react'

// Map emoji to icon component
const iconMap = {
  '📊': BarChart3,
  '📈': TrendingUp,
  '⚠️': AlertTriangle,
  '🎯': Target,
  '🔴': AlertCircle,
  '📤': Upload,
  '🏫': Building2,
  '🎓': GraduationCap,
  '📄': File,
  '📧': Mail,
  '🚪': LogOut,
  '👥': Users,
  '✓': Check,
  '✗': X,
  '❤️': Heart,
}

// Reusable Icon component
export function Icon({ emoji, size = 'md', color = 'currentColor' }) {
  const IconComponent = iconMap[emoji]
  
  if (!IconComponent) {
    // Fallback - return nothing if emoji not mapped
    return null
  }
  
  const sizeMap = {
    xs: 14,
    sm: 16,
    md: 20,
    lg: 24,
    xl: 32,
    '2xl': 40,
  }
  
  return (
    <IconComponent 
      size={sizeMap[size] || 20} 
      color={color}
      className="inline"
    />
  )
}

// Convenience components for common use cases
export const Icons = {
  Dashboard: (props) => <Icon emoji="📊" {...props} />,
  Progress: (props) => <Icon emoji="📈" {...props} />,
  Risk: (props) => <Icon emoji="⚠️" {...props} />,
  Target: (props) => <Icon emoji="🎯" {...props} />,
  AtRisk: (props) => <Icon emoji="🔴" {...props} />,
  Upload: (props) => <Icon emoji="📤" {...props} />,
  Courses: (props) => <Icon emoji="🏫" {...props} />,
  Education: (props) => <Icon emoji="🎓" {...props} />,
  PDF: (props) => <Icon emoji="📄" {...props} />,
  Email: (props) => <Icon emoji="📧" {...props} />,
  Logout: (props) => <Icon emoji="🚪" {...props} />,
  Users: (props) => <Icon emoji="👥" {...props} />,
  Success: (props) => <Icon emoji="✓" {...props} />,
  Failed: (props) => <Icon emoji="✗" {...props} />,
  Health: (props) => <Icon emoji="❤️" {...props} />,
}

export default Icon
