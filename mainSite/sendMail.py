import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from django.conf import settings
import os


class SendEmail():
    def __init__(self):
        """
        Инициализация класса для отправки email
        """
        pass
    
    def sendProjectApplication(self, project_data):
        """
        Отправка уведомления менеджеру о новом запросе на проект
        
        Args:
            project_data: объект Project с данными заказчика
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # Получаем конфигурацию email из настроек
            email_config = settings.PROJECT_APPLICATION_EMAIL_CONFIG
            
            # Проверяем наличие необходимых параметров
            if not email_config.get('send_to_email'):
                return {
                    'success': False,
                    'message': 'Email получателя не настроен в конфигурации'
                }
            
            # Создаем письмо
            msg = MIMEMultipart()
            msg['From'] = email_config['login']
            msg['To'] = email_config['send_to_email']
            msg['Subject'] = f'Новый запрос на реализацию проекта от {project_data.consumer_name}'
            
            # Формируем тело письма с информацией о заказчике
            body = f"""
Получен новый запрос на реализацию проекта!

ИНФОРМАЦИЯ О ЗАКАЗЧИКЕ:
Имя: {project_data.consumer_name}
Email: {project_data.consumer_email}
Телефон: {project_data.consumer_tel}
Сообщение: {project_data.consumer_message}

---
Это автоматическое уведомление с сайта.
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Подключаемся к SMTP серверу и отправляем письмо
            server = smtplib.SMTP(email_config['server'], 587)
            server.starttls()
            server.login(email_config['login'], email_config['password'])
            text = msg.as_string()
            server.sendmail(email_config['login'], email_config['send_to_email'], text)
            server.quit()
            
            return {
                'success': True,
                'message': 'Email успешно отправлен'
            }
            
        except smtplib.SMTPAuthenticationError:
            return {
                'success': False,
                'message': 'Ошибка аутентификации на SMTP сервере'
            }
        except smtplib.SMTPException as e:
            return {
                'success': False,
                'message': f'Ошибка SMTP: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Ошибка при отправке email: {str(e)}'
            }
    
    def sendJobApplication(self, candidate_data, job_data):
        """
        Отправка уведомления HR о новом отклике на вакансию
        
        Args:
            candidate_data: объект VacanciesApplication с данными кандидата
            job_data: объект Vacancies с данными о вакансии
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # Получаем конфигурацию email из настроек
            email_config = settings.JOB_APPLICATION_EMAIL_CONFIG
            
            # Проверяем наличие необходимых параметров
            if not email_config.get('send_to_email'):
                return {
                    'success': False,
                    'message': 'Email получателя не настроен в конфигурации'
                }
            
            # Создаем письмо
            msg = MIMEMultipart()
            msg['From'] = email_config['login']
            msg['To'] = email_config['send_to_email']
            msg['Subject'] = f'Новый отклик на вакансию: {job_data.title}'
            
            # Формируем тело письма с информацией о кандидате
            body = f"""
Получен новый отклик на вакансию!

ИНФОРМАЦИЯ О ВАКАНСИИ:
Должность: {job_data.title}
Регион: {job_data.region}
График работы: {job_data.work_schedule}
Зарплата: {job_data.salary} руб.

ИНФОРМАЦИЯ О КАНДИДАТЕ:
ФИО: {candidate_data.candidate_name}
Email: {candidate_data.candidate_email}
Телефон: {candidate_data.candidate_tel}
Дата и место рождения: {candidate_data.candidate_birthday}
Место жительства: {candidate_data.candidate_adress}
Уровень образования: {candidate_data.candidate_education_level}
Дополнительное образование: {candidate_data.candidate_subeducation_level}
Семейное положение: {candidate_data.candidate_marital_status}
Желаемый доход: {candidate_data.candidate_desire_income} руб.
Дополнительная информация: {candidate_data.candidate_information}

---
Это автоматическое уведомление с сайта.
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Прикрепляем резюме, если оно есть
            if candidate_data.candidate_resume:
                try:
                    filename = os.path.basename(candidate_data.candidate_resume.name)
                    with open(candidate_data.candidate_resume.path, 'rb') as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {filename}',
                        )
                        msg.attach(part)
                except Exception as e:
                    print(f'Ошибка при прикреплении файла: {str(e)}')
            
            # Подключаемся к SMTP серверу и отправляем письмо
            server = smtplib.SMTP(email_config['server'], 587)
            server.starttls()
            server.login(email_config['login'], email_config['password'])
            text = msg.as_string()
            server.sendmail(email_config['login'], email_config['send_to_email'], text)
            server.quit()
            
            return {
                'success': True,
                'message': 'Email успешно отправлен'
            }
            
        except smtplib.SMTPAuthenticationError:
            return {
                'success': False,
                'message': 'Ошибка аутентификации на SMTP сервере'
            }
        except smtplib.SMTPException as e:
            return {
                'success': False,
                'message': f'Ошибка SMTP: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Ошибка при отправке email: {str(e)}'
            }
