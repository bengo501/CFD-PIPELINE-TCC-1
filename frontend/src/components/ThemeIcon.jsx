import { useTheme } from '../context/ThemeContext';

/**
 * componente para exibir ícones que mudam conforme o tema
 * 
 * uso:
 * <ThemeIcon light="blenderLight.png" dark="blenderDark.png" alt="blender" />
 */
export default function ThemeIcon({ light, dark, alt, className = '', style = {} }) {
  const { theme } = useTheme();
  
  const iconSrc = theme === 'light' ? `/image/${light}` : `/image/${dark}`;
  
  return (
    <img 
      src={iconSrc} 
      alt={alt} 
      className={className}
      style={style}
    />
  );
}
