# manage.py
from flask_migrate import Migrate
from flask.cli import with_appcontext, FlaskGroup
import click
from backend.app import create_app, db
from backend.utils.backup import BackupManager

app = create_app()
migrate = Migrate(app, db)
cli = FlaskGroup(app)

@cli.command('backup')
@click.option('--tipo', '-t', 
              type=click.Choice(['completo', 'dados', 'arquivos']), 
              default='completo',
              help='Tipo de backup a ser realizado')
def fazer_backup(tipo):
    """Executa backup manual do sistema."""
    backup_manager = BackupManager(app.config)
    
    click.echo(f'Iniciando backup {tipo}...')
    
    try:
        if tipo == 'completo':
            success = backup_manager.fazer_backup()
        elif tipo == 'dados':
            success = backup_manager.fazer_backup_dados()
        else:  # arquivos
            success = backup_manager.fazer_backup_arquivos()
            
        if success:
            click.echo('Backup realizado com sucesso!')
        else:
            click.echo('Erro ao realizar backup. Verifique os logs para mais detalhes.')
            
    except Exception as e:
        click.echo(f'Erro ao realizar backup: {str(e)}')

if __name__ == '__main__':
    cli()  # Mudamos de app.run() para cli()