import re
from pathlib import Path
from typing import List, Tuple, Union

class SubtitleConverter:
    def __init__(self):
        self.time_pattern = re.compile(r'(\d{1,2}):(\d{1,2}):(\d{1,2})[,.](\d{1,3})')
        self.srt_time_pattern = re.compile(r'(\d{1,2}):(\d{1,2}):(\d{1,2}),(\d{1,3})')
        self.vtt_time_pattern = re.compile(r'(\d{1,2}):(\d{1,2}):(\d{1,2})\.(\d{1,3})')
        self.lrc_time_pattern = re.compile(r'\[(\d{1,2}):(\d{1,2})\.(\d{1,2})\]')

    def parse_time(self, time_str: str, format: str) -> float:
        """将时间字符串转换为秒数"""
        if format in ('srt', 'vtt'):
            match = self.time_pattern.match(time_str)
            if match:
                h, m, s, ms = map(int, match.groups())
                return h * 3600 + m * 60 + s + ms / 1000
        elif format == 'lrc':
            match = self.lrc_time_pattern.match(time_str)
            if match:
                m, s, cs = map(int, match.groups())
                return m * 60 + s + cs / 100
        return 0.0

    def format_time(self, seconds: float, target_format: str) -> str:
        """将秒数格式化为目标格式的时间字符串"""
        if target_format == 'srt':
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            ms = int((seconds - int(seconds)) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
        elif target_format == 'vtt':
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            ms = int((seconds - int(seconds)) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"
        elif target_format == 'lrc':
            m = int(seconds // 60)
            s = int(seconds % 60)
            cs = int((seconds - int(seconds)) * 100)
            return f"[{m:02d}:{s:02d}.{cs:02d}]"
        return ""

    def read_file(self, file_path: Union[str, Path]) -> Tuple[str, List[Tuple[float, float, str]]]:
        """读取字幕文件并返回格式和内容"""
        file_path = Path(file_path)
        content = file_path.read_text(encoding='utf-8').strip()
        lines = content.split('\n')
        
        if file_path.suffix.lower() == '.srt':
            return self.parse_srt(lines)
        elif file_path.suffix.lower() == '.vtt':
            return self.parse_vtt(lines)
        elif file_path.suffix.lower() == '.lrc':
            return self.parse_lrc(lines)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

    def parse_srt(self, lines: List[str]) -> Tuple[str, List[Tuple[float, float, str]]]:
        """解析SRT格式"""
        subtitles = []
        i = 0
        while i < len(lines):
            if lines[i].strip().isdigit():  # 序号行
                i += 1
                time_line = lines[i].strip()
                times = time_line.split(' --> ')
                if len(times) == 2:
                    start = self.parse_time(times[0].strip(), 'srt')
                    end = self.parse_time(times[1].strip(), 'srt')
                    i += 1
                    text_lines = []
                    while i < len(lines) and lines[i].strip():
                        text_lines.append(lines[i].strip())
                        i += 1
                    text = '\n'.join(text_lines)
                    subtitles.append((start, end, text))
            i += 1
        return 'srt', subtitles

    def parse_vtt(self, lines: List[str]) -> Tuple[str, List[Tuple[float, float, str]]]:
        """解析VTT格式"""
        subtitles = []
        i = 0
        while i < len(lines):
            if '-->' in lines[i]:  # 时间行
                time_line = lines[i].strip()
                times = time_line.split(' --> ')
                if len(times) == 2:
                    start = self.parse_time(times[0].strip(), 'vtt')
                    end = self.parse_time(times[1].strip(), 'vtt')
                    i += 1
                    text_lines = []
                    while i < len(lines) and lines[i].strip():
                        text_lines.append(lines[i].strip())
                        i += 1
                    text = '\n'.join(text_lines)
                    subtitles.append((start, end, text))
            i += 1
        return 'vtt', subtitles

    def parse_lrc(self, lines: List[str]) -> Tuple[str, List[Tuple[float, float, str]]]:
        """解析LRC格式"""
        subtitles = []
        time_text_map = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 查找所有时间标签
            time_tags = self.lrc_time_pattern.findall(line)
            if not time_tags:
                continue
                
            # 获取文本内容（去除时间标签后的部分）
            text = self.lrc_time_pattern.sub('', line).strip()
            
            for tag in time_tags:
                m, s, cs = map(int, tag)
                seconds = m * 60 + s + cs / 100
                time_text_map[seconds] = text
                
        # 将时间点排序并创建字幕条目
        sorted_times = sorted(time_text_map.keys())
        for i in range(len(sorted_times)):
            start = sorted_times[i]
            end = sorted_times[i + 1] if i + 1 < len(sorted_times) else start + 5  # 默认5秒
            text = time_text_map[start]
            subtitles.append((start, end, text))
            
        return 'lrc', subtitles

    def convert(self, input_file: Union[str, Path], output_format: str) -> str:
        """转换字幕文件格式"""
        input_format, subtitles = self.read_file(input_file)
        
        if input_format == output_format:
            raise ValueError("Input and output formats are the same")
            
        if output_format == 'srt':
            return self.to_srt(subtitles)
        elif output_format == 'vtt':
            return self.to_vtt(subtitles)
        elif output_format == 'lrc':
            return self.to_lrc(subtitles)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    def to_srt(self, subtitles: List[Tuple[float, float, str]]) -> str:
        """转换为SRT格式"""
        output = []
        for i, (start, end, text) in enumerate(subtitles, 1):
            start_str = self.format_time(start, 'srt')
            end_str = self.format_time(end, 'srt')
            output.append(f"{i}\n{start_str} --> {end_str}\n{text}\n")
        return '\n'.join(output)

    def to_vtt(self, subtitles: List[Tuple[float, float, str]]) -> str:
        """转换为VTT格式"""
        output = ["WEBVTT", ""]
        for start, end, text in subtitles:
            start_str = self.format_time(start, 'vtt')
            end_str = self.format_time(end, 'vtt')
            output.append(f"{start_str} --> {end_str}\n{text}\n")
        return '\n'.join(output)

    def to_lrc(self, subtitles: List[Tuple[float, float, str]]) -> str:
        """转换为LRC格式"""
        output = []
        for start, _, text in subtitles:
            time_str = self.format_time(start, 'lrc')
            output.append(f"{time_str}{text}")
        return '\n'.join(output)

    def convert_file(self, input_file: Union[str, Path], output_format: str):
        """转换文件并保存，自动生成输出文件名"""
        input_path = Path(input_file)
        
        # 生成输出文件名（相同路径，相同主文件名，新扩展名）
        output_file = input_path.with_suffix(f'.{output_format.lower()}')
        
        converted_content = self.convert(input_file, output_format)
        output_file.write_text(converted_content, encoding='utf-8')
        return output_file


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert between subtitle formats (SRT, VTT, LRC)")
    parser.add_argument("input_file", help="Input subtitle file (SRT, VTT or LRC)")
    parser.add_argument("output_format", help="Output format (srt, vtt or lrc)", 
                        choices=['srt', 'vtt', 'lrc'])
    
    args = parser.parse_args()
    
    converter = SubtitleConverter()
    try:
        output_file = converter.convert_file(args.input_file, args.output_format)
        print(f"Successfully converted {args.input_file} to {output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")