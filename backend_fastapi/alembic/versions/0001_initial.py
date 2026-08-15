"""Initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-08-14
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create roles table
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=50), nullable=False, unique=True),
    )

    # users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=254), nullable=False, unique=True, index=True),
        sa.Column("name", sa.String(length=200), nullable=True),
        sa.Column("hashed_password", sa.String(length=512), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    # association user_roles
    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id"), primary_key=True),
    )

    # diseases
    op.create_table(
        "diseases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
    )

    # disease_metadata
    op.create_table(
        "disease_metadata",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("disease_id", sa.Integer(), sa.ForeignKey("diseases.id"), nullable=True, unique=True),
        sa.Column("medications", sa.JSON(), nullable=True),
        sa.Column("diets", sa.JSON(), nullable=True),
        sa.Column("workouts", sa.JSON(), nullable=True),
        sa.Column("precautions", sa.JSON(), nullable=True),
        sa.Column("extra", sa.JSON(), nullable=True),
    )

    # symptoms
    op.create_table(
        "symptoms",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
    )

    # patients
    op.create_table(
        "patients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("sex", sa.String(length=16), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    # patient_symptoms
    op.create_table(
        "patient_symptoms",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("symptom_id", sa.Integer(), sa.ForeignKey("symptoms.id"), nullable=False),
        sa.Column("value", sa.Integer(), nullable=True),
    )

    # predictions
    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id"), nullable=True),
        sa.Column("input_vector", sa.JSON(), nullable=True),
        sa.Column("predicted_disease", sa.String(length=255), nullable=True),
        sa.Column("probabilities", sa.JSON(), nullable=True),
        sa.Column("explainability", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    # model_versions
    op.create_table(
        "model_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=True),
        sa.Column("path", sa.String(length=1024), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    # training_reports
    op.create_table(
        "training_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.String(length=128), nullable=True, unique=True),
        sa.Column("summary", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    # user_activity
    op.create_table(
        "user_activity",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("event_type", sa.String(length=128), nullable=True),
        sa.Column("event_payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    # recommendations
    op.create_table(
        "recommendations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id"), nullable=True),
        sa.Column("items", sa.JSON(), nullable=True),
        sa.Column("model_version_id", sa.Integer(), sa.ForeignKey("model_versions.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table("recommendations")
    op.drop_table("user_activity")
    op.drop_table("training_reports")
    op.drop_table("model_versions")
    op.drop_table("predictions")
    op.drop_table("patient_symptoms")
    op.drop_table("patients")
    op.drop_table("symptoms")
    op.drop_table("disease_metadata")
    op.drop_table("diseases")
    op.drop_table("user_roles")
    op.drop_table("users")
    op.drop_table("roles")
