# backend/utils/backup.py
import os
import shutil
from datetime import datetime
import schedule
import time
import subprocess
import logging
from threading import Thread

# Configuração do logging
logging.basicConfig(
    filename='backup.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BackupManager:
    def __init__(self, app_config):
        self.backup_dir = app_config.get('BACKUP_DIR', 'backups/')
        self.db_uri = app_config.get('SQLALCHEMY_DATABASE_URI')
        self.upload_dir = app_config.get('UPLOAD_FOLDER')
        self.max_backups = app_config.get('MAX_BACKUPS', 7)
        
        # Criar diretório de backup se não existir
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def fazer_backup(self):
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Backup do banco de dados
            db_file = f'backup_db_{timestamp}.sql'
            db_path = os.path.join(self.backup_dir, db_file)
            
            if 'postgresql' in self.db_uri:
                self._backup_postgres(db_path)
            elif 'mysql' in self.db_uri:
                self._backup_mysql(db_path)
            elif 'sqlite' in self.db_uri:
                self._backup_sqlite(db_path)
            
            # Backup dos arquivos de upload
            if self.upload_dir and os.path.exists(self.upload_dir):
                uploads_file = f'backup_uploads_{timestamp}.zip'
                uploads_path = os.path.join(self.backup_dir, uploads_file)
                self._backup_uploads(uploads_path)
            
            # Limpar backups antigos
            self._limpar_backups_antigos()
            
            logging.info(f'Backup completo realizado com sucesso: {timestamp}')
            return True
            
        except Exception as e:
            logging.error(f'Erro ao realizar backup: {str(e)}')
            return False
    
    def _backup_postgres(self, output_file):
        db_url = self.db_uri.replace('postgresql://', '').split('/')
        db_info = db_url[0].split('@')
        db_auth = db_info[0].split(':')
        
        env = os.environ.copy()
        env['PGPASSWORD'] = db_auth[1]
        
        subprocess.run([
            'pg_dump',
            '-h', db_info[1].split(':')[0],
            '-U', db_auth[0],
            '-d', db_url[1],
            '-f', output_file
        ], env=env, check=True)
    
    def _backup_mysql(self, output_file):
        # Implementar backup MySQL se necessário
        pass
    
    def _backup_sqlite(self, output_file):
        db_path = self.db_uri.replace('sqlite:///', '')
        shutil.copy2(db_path, output_file)
    
    def _backup_uploads(self, output_file):
        shutil.make_archive(
            output_file.replace('.zip', ''),
            'zip',
            self.upload_dir
        )
    
    def _limpar_backups_antigos(self):
        files = []
        for f in os.listdir(self.backup_dir):
            path = os.path.join(self.backup_dir, f)
            files.append((path, os.path.getctime(path)))
        
        # Ordenar por data de criação
        files.sort(key=lambda x: x[1], reverse=True)
        
        # Manter apenas os últimos MAX_BACKUPS
        for file_path, _ in files[self.max_backups * 2:]:  # *2 porque temos DB e uploads
            try:
                os.remove(file_path)
                logging.info(f'Backup antigo removido: {file_path}')
            except Exception as e:
                logging.error(f'Erro ao remover backup antigo {file_path}: {str(e)}')

def iniciar_agendador_backup(app_config):
    backup_manager = BackupManager(app_config)
    
    def job():
        backup_manager.fazer_backup()
    
    # Agendar backup diário às 23h
    schedule.every().day.at("23:00").do(job)
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    # Iniciar o agendador em uma thread separada
    thread = Thread(target=run_scheduler, daemon=True)
    thread.start()
    
    return backup_manager

