from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import pandas as pd
from .models import UserTargetUpload, DbtRunLog
from datetime import datetime
import logging
import subprocess
import os
from pathlib import Path
import threading
import time

logger = logging.getLogger(__name__)

def run_dbt_async(dbt_log_id, triggered_by='upload'):
    """
    Menjalankan dbt run secara async di background thread
    """
    try:
        dbt_log = DbtRunLog.objects.get(id=dbt_log_id)
        dbt_log.status = 'running'
        dbt_log.save()
        
        start_time = time.time()
        
        # Set working directory ke /app (root project)
        dbt_project_dir = Path('/app')
        
        # Set environment variables untuk dbt
        env = os.environ.copy()
        env['DBT_PROFILES_DIR'] = '/app/dbt_profiles'
        
        # Jalankan dbt run
        logger.info(f"Memulai dbt run (log_id: {dbt_log_id})...")
        result = subprocess.run(
            ['dbt', 'run', '--project-dir', str(dbt_project_dir)],
            cwd=str(dbt_project_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=300  # Timeout 5 menit
        )
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            logger.info(f"dbt run berhasil! (log_id: {dbt_log_id})")
            dbt_log.status = 'success'
            dbt_log.output = result.stdout
            dbt_log.error = None
            dbt_log.completed_at = datetime.now()
            dbt_log.duration_seconds = duration
            dbt_log.save()
        else:
            logger.error(f"dbt run gagal (log_id: {dbt_log_id}): {result.stderr}")
            dbt_log.status = 'failed'
            dbt_log.output = result.stdout
            dbt_log.error = result.stderr
            dbt_log.completed_at = datetime.now()
            dbt_log.duration_seconds = duration
            dbt_log.save()
            
    except subprocess.TimeoutExpired:
        logger.error(f"dbt run timeout (log_id: {dbt_log_id})")
        dbt_log.status = 'failed'
        dbt_log.error = 'Timeout setelah 5 menit'
        dbt_log.completed_at = datetime.now()
        dbt_log.duration_seconds = 300
        dbt_log.save()
    except Exception as e:
        logger.error(f"Error menjalankan dbt (log_id: {dbt_log_id}): {e}", exc_info=True)
        dbt_log.status = 'failed'
        dbt_log.error = str(e)
        dbt_log.completed_at = datetime.now()
        if 'start_time' in locals():
            dbt_log.duration_seconds = time.time() - start_time
        dbt_log.save()


def run_dbt_sync():
    """
    Menjalankan dbt run secara synchronous (untuk backward compatibility)
    """
    try:
        # Set working directory ke /app (root project)
        dbt_project_dir = Path('/app')
        
        # Set environment variables untuk dbt
        env = os.environ.copy()
        env['DBT_PROFILES_DIR'] = '/app/dbt_profiles'
        
        # Jalankan dbt run
        logger.info("Memulai dbt run...")
        result = subprocess.run(
            ['dbt', 'run', '--project-dir', str(dbt_project_dir)],
            cwd=str(dbt_project_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=300  # Timeout 5 menit
        )
        
        if result.returncode == 0:
            logger.info("dbt run berhasil!")
            logger.info(f"Output: {result.stdout}")
            return {
                'success': True,
                'message': 'dbt run berhasil dijalankan',
                'output': result.stdout,
                'error': None
            }
        else:
            logger.error(f"dbt run gagal: {result.stderr}")
            return {
                'success': False,
                'message': 'dbt run gagal',
                'output': result.stdout,
                'error': result.stderr
            }
            
    except subprocess.TimeoutExpired:
        logger.error("dbt run timeout setelah 5 menit")
        return {
            'success': False,
            'message': 'dbt run timeout',
            'output': None,
            'error': 'Timeout setelah 5 menit'
        }
    except Exception as e:
        logger.error(f"Error menjalankan dbt: {e}", exc_info=True)
        return {
            'success': False,
            'message': f'Error menjalankan dbt: {str(e)}',
            'output': None,
            'error': str(e)
        }

def upload_csv(request): 
    message = None
    message_type = None  # 'success' or 'error'
    preview_data = None
    preview_columns = None
    table_name = None
    total_rows = 0
    dbt_result = None
    
    if request.method == 'POST':
        if not request.FILES.get("file"):
            message = "Error: Tidak ada file yang diupload."
            message_type = 'error'
        else:
            try:
                file = request.FILES.get("file")
                logger.info(f"File diterima: {file.name}, size: {file.size}")
                
                # Reset file pointer untuk membaca ulang
                file.seek(0)
                
                # Baca CSV
                df = pd.read_csv(file)
                logger.info(f"CSV berhasil dibaca. Jumlah baris: {len(df)}")
                logger.info(f"Kolom yang ada: {list(df.columns)}")
                
                # Validasi kolom yang diperlukan
                required_column = 'order_delivered_carrier_date'
                if required_column not in df.columns:
                    message = f"Error: Kolom '{required_column}' tidak ditemukan dalam CSV. Kolom yang ada: {', '.join(df.columns)}"
                    message_type = 'error'
                else:
                    # Simpan preview data sebelum modifikasi
                    df_preview = df.copy()
                    
                    # Konversi ke datetime
                    df[required_column] = pd.to_datetime(
                        df[required_column], 
                        errors='coerce'
                    )
                    
                    # Hapus baris dengan tanggal tidak valid
                    rows_before = len(df)
                    df.dropna(subset=[required_column], inplace=True)
                    rows_after = len(df)
                    
                    logger.info(f"Baris setelah dropna: {rows_after} dari {rows_before}")
                    
                    if rows_after == 0:
                        message = "Error: Tidak ada data valid setelah pembersihan. Pastikan kolom 'order_delivered_carrier_date' berisi tanggal yang valid."
                        message_type = 'error'
                    else:
                        # Buat list untuk bulk_create
                        upload_list = []
                        for _, row in df.iterrows():
                            try:
                                date_value = row[required_column].date()
                                upload_list.append(
                                    UserTargetUpload(
                                        month=date_value,
                                        target_amount=1  
                                    )
                                )
                            except Exception as e:
                                logger.warning(f"Error memproses baris: {e}")
                                continue
                        
                        if len(upload_list) == 0:
                            message = "Error: Tidak ada data yang bisa disimpan."
                            message_type = 'error'
                        else:
                            # Simpan ke database
                            UserTargetUpload.objects.bulk_create(upload_list)
                            total_rows = len(upload_list)
                            logger.info(f"Berhasil menyimpan {total_rows} data")
                            
                            # Buat log entry untuk dbt run (dengan error handling)
                            dbt_log = None
                            try:
                                dbt_log = DbtRunLog.objects.create(
                                    status='pending',
                                    triggered_by='upload'
                                )
                                
                                # Jalankan dbt secara async di background
                                logger.info(f"Memanggil dbt untuk memproses data (log_id: {dbt_log.id})...")
                                thread = threading.Thread(
                                    target=run_dbt_async,
                                    args=(dbt_log.id, 'upload'),
                                    daemon=True
                                )
                                thread.start()
                                
                                message = f"Upload berhasil! {total_rows} data telah disimpan ke database. dbt pipeline sedang berjalan di background..."
                            except Exception as e:
                                logger.warning(f"Tabel dbt_run_logs belum ada. Jalankan migration: {e}")
                                # Fallback: jalankan dbt secara sync jika tabel belum ada
                                logger.info("Menjalankan dbt secara synchronous...")
                                dbt_result = run_dbt_sync()
                                if dbt_result['success']:
                                    message = f"Upload berhasil! {total_rows} data telah disimpan ke database. dbt run berhasil dijalankan."
                                else:
                                    message = f"Upload berhasil! {total_rows} data telah disimpan ke database. Namun dbt run gagal: {dbt_result.get('error', 'Unknown error')}"
                            
                            message_type = 'success'
                            
                            # Siapkan preview data untuk ditampilkan
                            # Ambil 5 baris pertama dari data yang valid
                            df_preview[required_column] = pd.to_datetime(
                                df_preview[required_column], 
                                errors='coerce'
                            )
                            df_preview_valid = df_preview.dropna(subset=[required_column]).head(5)
                            
                            # Konversi ke format yang bisa ditampilkan di template
                            preview_columns = list(df_preview_valid.columns)
                            preview_data = []
                            for _, row in df_preview_valid.iterrows():
                                row_dict = {}
                                for col in preview_columns:
                                    val = row[col]
                                    # Format datetime untuk tampilan
                                    if pd.isna(val):
                                        row_dict[col] = '-'
                                    elif isinstance(val, pd.Timestamp):
                                        row_dict[col] = val.strftime('%Y-%m-%d %H:%M:%S')
                                    else:
                                        row_dict[col] = str(val)
                                preview_data.append(row_dict)
                            
                            # Nama tabel dari model
                            table_name = UserTargetUpload._meta.db_table
            
            except pd.errors.EmptyDataError:
                message = "Error: File CSV kosong atau tidak valid."
                message_type = 'error'
                logger.error("CSV kosong")
            except pd.errors.ParserError as e:
                message = f"Error: Format CSV tidak valid. {str(e)}"
                message_type = 'error'
                logger.error(f"Error parsing CSV: {e}")
            except Exception as e:
                message = f"Gagal upload: {str(e)}"
                message_type = 'error'
                logger.error(f"Error: {e}", exc_info=True)

    # Ambil latest dbt run log untuk ditampilkan (dengan error handling)
    latest_dbt_log = None
    try:
        latest_dbt_log = DbtRunLog.objects.first()
    except Exception as e:
        logger.warning(f"Tabel dbt_run_logs belum ada. Jalankan migration terlebih dahulu: {e}")
    
    # Ambil achievement metrics
    metrics = None
    try:
        metrics = get_achievement_metrics()
    except Exception as e:
        logger.warning(f"Error getting metrics: {e}")
        metrics = {
            'total_uploads': 0,
            'total_processed': 0,
            'success_rate': 0,
            'total_runs': 0,
            'success_count': 0,
            'latest_status': 'N/A',
            'latest_duration': None,
        }
    
    context = {
        "message": message,
        "message_type": message_type,
        "preview_data": preview_data,
        "preview_columns": preview_columns,
        "table_name": table_name,
        "total_rows": total_rows,
        "latest_dbt_log": latest_dbt_log,
        "metrics": metrics,
    }
    
    return render(request, "upload.html", context)


@require_http_methods(["POST"])
def rerun_pipeline(request):
    """Endpoint untuk re-run dbt pipeline"""
    try:
        # Buat log entry baru (dengan error handling)
        try:
            dbt_log = DbtRunLog.objects.create(
                status='pending',
                triggered_by='rerun'
            )
            
            # Jalankan dbt secara async
            thread = threading.Thread(
                target=run_dbt_async,
                args=(dbt_log.id, 'rerun'),
                daemon=True
            )
            thread.start()
            
            return JsonResponse({
                'success': True,
                'message': 'Pipeline sedang dijalankan di background',
                'log_id': dbt_log.id,
                'status': 'pending'
            })
        except Exception as table_error:
            # Jika tabel belum ada, jalankan secara sync
            logger.warning(f"Tabel dbt_run_logs belum ada: {table_error}")
            dbt_result = run_dbt_sync()
            return JsonResponse({
                'success': dbt_result['success'],
                'message': dbt_result['message'],
                'status': 'completed' if dbt_result['success'] else 'failed'
            })
    except Exception as e:
        logger.error(f"Error re-running pipeline: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


def get_dbt_status(request, log_id):
    """Endpoint untuk mendapatkan status dbt run"""
    try:
        dbt_log = get_object_or_404(DbtRunLog, id=log_id)
        return JsonResponse({
            'id': dbt_log.id,
            'status': dbt_log.status,
            'started_at': dbt_log.started_at.isoformat() if dbt_log.started_at else None,
            'completed_at': dbt_log.completed_at.isoformat() if dbt_log.completed_at else None,
            'duration_seconds': dbt_log.duration_seconds,
            'triggered_by': dbt_log.triggered_by,
        })
    except Exception as e:
        logger.error(f"Error getting dbt status: {e}", exc_info=True)
        # Jika tabel belum ada, return status not available
        if 'does not exist' in str(e) or 'relation' in str(e).lower():
            return JsonResponse({
                'success': False,
                'message': 'Tabel dbt_run_logs belum ada. Jalankan migration terlebih dahulu.',
                'status': 'not_available'
            }, status=404)
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


def get_achievement_metrics():
    """Menghitung achievement metrics dengan join sales data"""
    try:
        from django.db import connection
        
        # Query untuk achievement metrics
        with connection.cursor() as cursor:
            # Total data yang diupload
            try:
                cursor.execute("""
                    SELECT COUNT(*) as total_uploads
                    FROM raw_user_targets
                """)
                total_uploads = cursor.fetchone()[0]
            except:
                total_uploads = 0
            
            # Total data yang sudah diproses dbt
            try:
                cursor.execute("""
                    SELECT COUNT(*) as total_processed
                    FROM user_targets_clean
                """)
                total_processed = cursor.fetchone()[0]
            except:
                total_processed = 0
            
            # Success rate dbt runs (dengan error handling untuk tabel yang belum ada)
            success_count = 0
            total_runs = 0
            latest_status = 'N/A'
            latest_duration = None
            
            try:
                cursor.execute("""
                    SELECT 
                        COUNT(*) FILTER (WHERE status = 'success') as success_count,
                        COUNT(*) as total_runs
                    FROM dbt_run_logs
                """)
                result = cursor.fetchone()
                success_count = result[0] or 0
                total_runs = result[1] or 0
                success_rate = (success_count / total_runs * 100) if total_runs > 0 else 0
                
                # Latest dbt run status
                cursor.execute("""
                    SELECT status, duration_seconds
                    FROM dbt_run_logs
                    ORDER BY started_at DESC
                    LIMIT 1
                """)
                latest = cursor.fetchone()
                if latest:
                    latest_status = latest[0]
                    latest_duration = latest[1]
            except Exception as e:
                logger.warning(f"Tabel dbt_run_logs belum ada atau error: {e}")
                success_rate = 0
            
            return {
                'total_uploads': total_uploads,
                'total_processed': total_processed,
                'success_rate': round(success_rate, 2) if 'success_rate' in locals() else 0,
                'total_runs': total_runs,
                'success_count': success_count,
                'latest_status': latest_status,
                'latest_duration': latest_duration,
            }
    except Exception as e:
        logger.error(f"Error getting achievement metrics: {e}", exc_info=True)
        return {
            'total_uploads': 0,
            'total_processed': 0,
            'success_rate': 0,
            'total_runs': 0,
            'success_count': 0,
            'latest_status': 'Error',
            'latest_duration': None,
        }