from image_processor import ImageProcessor

def main():
    # 创建图片处理器实例
    processor = ImageProcessor()
    
    try:
        # 处理图片
        processor.process_image(
            input_path="test.jpg",
            output_path="output.jpg",
            crop_box=(100, 100, 500, 500),  # 裁剪区域
            new_size=(800, 600),            # 新尺寸
            quality=85                      # 压缩质量
        )
        print("图片处理成功！")
        
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    main() 