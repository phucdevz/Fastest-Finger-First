import json
import os

class ConfigLoader:
    @staticmethod
    def load_config():
        """Load cấu hình từ file config.json"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            print(f"Config file not found at {config_path}")
            return ConfigLoader.get_default_config()
        except json.JSONDecodeError as e:
            print(f"Error parsing config file: {e}")
            return ConfigLoader.get_default_config()
    
    @staticmethod
    def get_default_config():
        """Trả về cấu hình mặc định"""
        return {
            "server": {
                "host": "localhost",
                "port": 5000,
                "max_players": 4,
                "question_time": 30,
                "wait_time": 10
            },
            "client": {
                "host": "localhost",
                "port": 5000,
                "timeout": 5
            },
            "game": {
                "questions_per_round": 10,
                "points_per_correct": 10,
                "bonus_points_fast": 5
            },
            "ui": {
                "theme": "dark",
                "window_width": 1200,
                "window_height": 800,
                "font_family": "Arial",
                "font_size": 14
            }
        }
    
    @staticmethod
    def save_config(config):
        """Lưu cấu hình vào file"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False 