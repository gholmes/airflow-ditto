from datetime import timedelta

from airflow import DAG
from airflow.utils.trigger_rule import TriggerRule

from airflowhdi.operators.azure_hdinsight_create_cluster_operator import ConnectedAzureHDInsightCreateClusterOperator
from tests.test_commons import *
from ditto.templates.emr_hdi_template import EmrHdiDagTransformerTemplate
from ditto.transformers.emr import EmrCreateJobFlowOperatorTransformer
from ditto.api import TransformerDefaults, TransformerDefaultsConf
import tests.test_dags.complex_dag.emr_dag
import tests.test_dags.complex_dag.expected_hdi_dag


def transform_call(src_dag: DAG) -> DAG:
    create_cluster_op = ConnectedAzureHDInsightCreateClusterOperator(task_id="start_cluster",
                                                                     azure_conn_id=AZURE_CONN_ID,
                                                                     hdi_conn_id=HDI_CONN_ID,
                                                                     cluster_name=CLUSTER_NAME,
                                                                     trigger_rule=TriggerRule.ALL_SUCCESS)

    return EmrHdiDagTransformerTemplate(DAG(
        dag_id='HDI_emr_job_flow_manual_steps_dag',
        default_args=DEFAULT_DAG_ARGS,
        dagrun_timeout=timedelta(hours=2),
        max_active_runs=1,
        schedule_interval=None
    ), transformer_defaults=TransformerDefaultsConf({
        EmrCreateJobFlowOperatorTransformer: TransformerDefaults(
            default_operator=create_cluster_op)})).transform(src_dag)