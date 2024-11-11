from PIL import Image
import os
import io

class ImageProcessor:
    """图片处理器类，提供图片裁剪、调整大小和压缩功能"""
    
    def __init__(self):
        """初始化图片处理器"""
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.webp'}

    def _validate_input(self, input_path):
        """验证输入文件是否存在且格式受支持"""
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
        
        file_ext = os.path.splitext(input_path)[1].lower()
        if file_ext not in self.supported_formats:
            raise ValueError(f"不支持的文件格式: {file_ext}")

    def process_image(self, input_path, output_path, crop_box=None, new_size=None, quality=85, target_size=None):
        """
        处理图片：裁剪、调整大小和压缩
        
        参数:
            input_path (str): 输入图片路径
            output_path (str): 输出图片路径
            crop_box (tuple): 裁剪区域 (left, top, right, bottom)
            new_size (tuple): 新的图片尺寸 (width, height)
            quality (int): 压缩质量 (1-100)
            target_size (int): 目标文件大小（字节）
        """
        # 验证输入
        self._validate_input(input_path)
        
        try:
            # 打开图片
            with Image.open(input_path) as img:
                # 确保图片在RGB模式
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # 如果需要裁剪
                if crop_box:
                    img = img.crop(crop_box)
                
                # 如果需要调整大小
                if new_size:
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # 如果指定了目标大小，使用二分查找找到合适的质量值
                if target_size:
                    quality = self._find_quality_for_target_size(img, target_size)
                
                # 根据输出文件格式选择保存参数
                file_ext = os.path.splitext(output_path)[1].lower()
                save_params = self._get_save_params(file_ext, quality)
                
                # 保存处理后的图片
                img.save(output_path, **save_params)
                
        except Exception as e:
            raise Exception(f"处理图片时出错: {str(e)}")
    
    def _find_quality_for_target_size(self, img, target_size, tolerance=0.1):
        """使用二分查找找到接近目标大小的质量值"""
        min_q = 1
        max_q = 100
        best_q = 85
        best_size = float('inf')
        
        while min_q <= max_q:
            mid_q = (min_q + max_q) // 2
            current_size = self._get_file_size(img, mid_q)
            
            # 更新最佳质量值
            if abs(current_size - target_size) < abs(best_size - target_size):
                best_q = mid_q
                best_size = current_size
            
            # 如果当前大小在目标大小的容差范围内，返回当前质量值
            if abs(current_size - target_size) <= target_size * tolerance:
                return mid_q
            
            if current_size > target_size:
                max_q = mid_q - 1
            else:
                min_q = mid_q + 1
        
        return best_q
    
    def _get_file_size(self, img, quality):
        """获取指定质量值下的文件大小"""
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        return buffer.tell()
    
    def _get_save_params(self, file_ext, quality):
        """根据文件格式获取保存参数"""
        if file_ext in ['.jpg', '.jpeg']:
            return {
                'format': 'JPEG',
                'quality': quality,
                'optimize': True,
                'progressive': True
            }
        elif file_ext == '.png':
            return {
                'format': 'PNG',
                'optimize': True,
                'compress_level': 9
            }
        elif file_ext == '.webp':
            return {
                'format': 'WEBP',
                'quality': quality,
                'method': 6,
                'lossless': False
            }
        return {}