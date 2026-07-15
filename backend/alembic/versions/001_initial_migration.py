"""Initial migration - create all tables

Revision ID: 001
Revises:
Create Date: 2026-07-14

"""
from alembic import op
import sqlalchemy as sa

from app.core.db_types import get_uuid_column_type, get_json_column_type

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated ###
    op.create_table('users',
        sa.Column('id', get_uuid_column_type(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('nickname', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    op.create_table('jobs',
        sa.Column('id', get_uuid_column_type(), nullable=False),
        sa.Column('user_id', get_uuid_column_type(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('company', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('requirements', get_json_column_type(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_jobs_user_id'), 'jobs', ['user_id'], unique=False)

    op.create_table('resumes',
        sa.Column('id', get_uuid_column_type(), nullable=False),
        sa.Column('user_id', get_uuid_column_type(), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('minio_key', sa.String(length=500), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('parsed_data', get_json_column_type(), nullable=True),
        sa.Column('raw_text_hash', sa.String(length=64), nullable=True),
        sa.Column('parse_method', sa.String(length=50), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resumes_user_id'), 'resumes', ['user_id'], unique=False)

    op.create_table('applications',
        sa.Column('id', get_uuid_column_type(), nullable=False),
        sa.Column('user_id', get_uuid_column_type(), nullable=False),
        sa.Column('job_id', get_uuid_column_type(), nullable=True),
        sa.Column('company', sa.String(length=255), nullable=False),
        sa.Column('position', sa.String(length=255), nullable=False),
        sa.Column('stage', sa.String(length=50), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('salary_range', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('contact_info', sa.String(length=255), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_applications_user_id'), 'applications', ['user_id'], unique=False)

    op.create_table('interviews',
        sa.Column('id', get_uuid_column_type(), nullable=False),
        sa.Column('user_id', get_uuid_column_type(), nullable=False),
        sa.Column('resume_id', get_uuid_column_type(), nullable=True),
        sa.Column('job_id', get_uuid_column_type(), nullable=True),
        sa.Column('round', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interviews_user_id'), 'interviews', ['user_id'], unique=False)

    op.create_table('growth_records',
        sa.Column('id', get_uuid_column_type(), nullable=False),
        sa.Column('user_id', get_uuid_column_type(), nullable=False),
        sa.Column('interview_id', get_uuid_column_type(), nullable=True),
        sa.Column('dimension', sa.String(length=50), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_growth_records_user_id'), 'growth_records', ['user_id'], unique=False)

    op.create_table('messages',
        sa.Column('id', get_uuid_column_type(), nullable=False),
        sa.Column('interview_id', get_uuid_column_type(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('evaluation_id', get_uuid_column_type(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_interview_id'), 'messages', ['interview_id'], unique=False)

    op.create_table('evaluations',
        sa.Column('id', get_uuid_column_type(), nullable=False),
        sa.Column('interview_id', get_uuid_column_type(), nullable=False),
        sa.Column('dimension', sa.String(length=50), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_evaluations_interview_id'), 'evaluations', ['interview_id'], unique=False)

    op.create_table('reviews',
        sa.Column('id', get_uuid_column_type(), nullable=False),
        sa.Column('interview_id', get_uuid_column_type(), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('radar_data', get_json_column_type(), nullable=True),
        sa.Column('question_reviews', get_json_column_type(), nullable=True),
        sa.Column('interviewer_summary', sa.Text(), nullable=True),
        sa.Column('suggestions', get_json_column_type(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated ###
    op.drop_table('reviews')
    op.drop_index(op.f('ix_evaluations_interview_id'), table_name='evaluations')
    op.drop_table('evaluations')
    op.drop_index(op.f('ix_messages_interview_id'), table_name='messages')
    op.drop_table('messages')
    op.drop_index(op.f('ix_growth_records_user_id'), table_name='growth_records')
    op.drop_table('growth_records')
    op.drop_index(op.f('ix_interviews_user_id'), table_name='interviews')
    op.drop_table('interviews')
    op.drop_index(op.f('ix_applications_user_id'), table_name='applications')
    op.drop_table('applications')
    op.drop_index(op.f('ix_resumes_user_id'), table_name='resumes')
    op.drop_table('resumes')
    op.drop_index(op.f('ix_jobs_user_id'), table_name='jobs')
    op.drop_table('jobs')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
