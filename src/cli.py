# src/cli.py
"""
コマンドラインインターフェース
"""

import sys
import os
import argparse
import logging

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import Spec2Clouds

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def main():
    """CLIエントリポイント"""
    spec2Clouds = argparse.ArgumentParser(
        description='Excel Parser - Convert Excel files to JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.cli                    # Use default config/config.yaml
  python -m src.cli config/settings.yaml  # Use specific config
  python -m src.cli --debug            # Enable debug logging
  python -m src.cli --validate-only    # Only validate config
        """
    )

    spec2Clouds.add_argument(
        'config',
        nargs='?',
        default='config/settings.yaml',
        help='Path to configuration file (default: config/settings.yaml)'
    )

    spec2Clouds.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    spec2Clouds.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate configuration and exit'
    )

    spec2Clouds.add_argument(
        '--version',
        action='version',
        version='Excel Parser 2.0.0'
    )

    args = spec2Clouds.parse_args()

    # バリデーションのみの実行
    if args.validate_only:
        from src.core.config_validator import ConfigValidator
        config = ConfigValidator.load_and_validate(args.config, exit_on_error=True)
        if config:
            print("✅ Configuration is valid!")
        return

    # 通常実行
    try:
        spec2Clouds_obj = Spec2Clouds(args.config, debug=args.debug)
        spec2Clouds_obj.run()
        sys.exit(0)
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=args.debug)
        sys.exit(1)


if __name__ == '__main__':
    main()
