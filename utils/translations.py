"""
Translation Module for Streamlit App
Bilingual support: English (EN) and Portuguese Brazil (PT-BR)
"""

TRANSLATIONS = {
    'en': {
        # Common strings
        'common': {
            'language': 'Language',
            'english': 'English',
            'portuguese': 'Português (BR)',
            'success': 'Success',
            'error': 'Error',
            'warning': 'Warning',
            'loading': 'Loading',
            'download': 'Download',
            'upload': 'Upload',
            'prediction': 'Prediction',
            'results': 'Results',
            'features': 'Features',
            'required': 'Required',
            'optional': 'Optional',
            'missing': 'Missing',
            'devices': 'Devices',
            'device': 'Device',
        },
        
        # Sidebar
        'sidebar': {
            'title': '🔧 IoT Device Prediction',
            'model_version': 'Model Version',
            'training_date': 'Training Date',
            'algorithm': 'Algorithm',
            'recall': 'Recall',
            'precision': 'Precision',
            'f1_score': 'F1-Score',
            'recall_delta': 'vs baseline',
            'precision_delta': 'vs target',
        },
        
        # Home Page
        'home': {
            'title': '🏠 IoT Critical Device Prediction',
            'subtitle': 'Machine Learning Model for Preventive Maintenance',
            'performance_title': '📈 Model Performance Highlights',
            'recall_label': 'Recall',
            'recall_help': 'Percentage of critical devices correctly detected (11/14)',
            'precision_label': 'Precision',
            'precision_help': 'Accuracy of critical predictions (only 2 false alarms)',
            'f1_label': 'F1-Score',
            'f1_help': 'Balanced measure of precision and recall',
            'auc_label': 'ROC-AUC',
            'auc_help': 'Area under ROC curve - overall model discriminative power',
            'objective_title': '🎯 Project Objective',
            'objective_text': """
            Predict **critical IoT devices** before failure to enable **preventive maintenance** 
            and avoid unplanned downtime. The model analyzes **29 telemetry features** from 
            **789 deployed devices** to identify the **5.7%** at risk of critical failure.
            """,
            'why_title': '💡 Why This Matters',
            'why_unplanned': '**Unplanned downtime** costs 3-5x more than preventive maintenance',
            'why_emergency': '**Emergency repairs** disrupt operations and customer satisfaction',
            'why_early': '**Early detection** enables scheduled maintenance during optimal windows',
            'why_resource': '**Resource optimization** - focus maintenance efforts on high-risk devices',
            'approach_title': '🔬 Technical Approach',
            'approach_text': """
            **Algorithm:** CatBoost with SMOTE oversampling
            
            **Challenge:** Severe class imbalance (16.8:1 ratio - only 45 critical in 789 devices)
            
            **Solution:** Strategic data balancing with SMOTE while preventing data leakage
            
            **Key Discovery:** CatBoost's ordered boosting + categorical features outperformed 
            XGBoost and LightGBM for this imbalanced telemetry data
            """,
            'results_title': '📊 Key Results',
            'results_recall': '**78.6% Recall** - 11 of 14 critical devices detected in test set',
            'results_precision': '**84.6% Precision** - Only 2 false alarms (manageable overhead)',
            'results_target': '**Exceeds 80% target** - Precision surpasses business requirement',
            'results_f1': '**81.5% F1-Score** - Strong balanced performance',
            'deployment_title': '🚀 Deployment Ready',
            'deployment_text': """
            The model is **production-ready** and available through this web interface:
            
            - **Batch Upload**: Process multiple devices from CSV
            - **Single Prediction**: Interactive assessment for individual devices
            - **Model Insights**: Explore performance metrics and feature importance
            - **Research Context**: Understand the methodology and discoveries
            """,
            'nav_title': '📍 Quick Navigation',
            'nav_batch': '**Batch Upload** - Upload CSV with multiple devices',
            'nav_single': '**Single Prediction** - Enter features manually for one device',
            'nav_insights': '**Model Insights** - Explore confusion matrix and feature importance',
            'nav_research': '**Research Context** - Learn about the problem and approach',
        },
        
        # Batch Upload Page
        'batch': {
            'title': '📤 Batch Upload - Bulk Device Prediction',
            'subtitle': 'Upload a CSV file with device features to get predictions for multiple devices at once.',
            'requirements_title': '📋 CSV Format Requirements',
            'requirements_intro': 'Your CSV must contain **29 required features**:',
            'requirements_telemetry': 'Telemetry Features (18)',
            'requirements_telemetry_optical': '`optical_*`: mean, std, min, max, readings, below_threshold, range',
            'requirements_telemetry_temp': '`temp_*`: mean, std, min, max, above_threshold, range',
            'requirements_telemetry_battery': '`battery_*`: mean, std, min, max, below_threshold',
            'requirements_connectivity': 'Connectivity Features (9)',
            'requirements_connectivity_snr': '`snr_*`: mean, std, min',
            'requirements_connectivity_rsrp': '`rsrp_*`: mean, std, min',
            'requirements_connectivity_rsrq': '`rsrq_*`: mean, std, min',
            'requirements_messaging': 'Messaging Features (2)',
            'requirements_messaging_list': '`total_messages`, `max_frame_count`',
            'requirements_optional': '**Optional columns:** `device_id` (for identification, not used in prediction)',
            'requirements_missing': '**Missing values:** OK - model has built-in imputation (median strategy)',
            'template_button': '📥 Download Example CSV Template',
            'template_download': '💾 Download template.csv',
            'upload_label': 'Upload your CSV file',
            'upload_help': 'CSV with device features (one row per device)',
            'loaded_success': '✅ Loaded {count} devices from CSV',
            'preview_title': '👀 Preview Data (first 5 rows)',
            'validation_error': '❌ Cannot proceed - {count} required features missing',
            'predict_button': '🚀 Generate Predictions',
            'predicting': '🔄 Generating predictions for {count} devices...',
            'complete_success': '✅ Predictions complete!',
            'summary_title': '📊 Prediction Summary',
            'summary_total': 'Total Devices Analyzed',
            'summary_critical': 'Predicted Critical',
            'summary_normal': 'Predicted Normal',
            'summary_critical_pct': '{pct}% critical rate',
            'results_title': '📋 Detailed Results',
            'results_help': 'Sort by probability to see highest-risk devices first',
            'download_button': '💾 Download Results CSV',
            'download_filename': 'predictions_results.csv',
            'column_device_id': 'device_id',
            'column_prediction': 'prediction',
            'column_probability': 'critical_probability',
            'column_risk_level': 'risk_level',
            'prediction_critical': 'CRITICAL',
            'prediction_normal': 'NORMAL',
            'risk_high': 'HIGH',
            'risk_medium': 'MEDIUM',
            'risk_low': 'LOW',
        },
        
        # Single Prediction Page
        'single': {
            'title': '🔍 Single Device Prediction',
            'subtitle': 'Enter features for a single device to get instant risk assessment and recommendations.',
            'form_title': '📝 Device Features Input',
            'tab_telemetry': '📡 Telemetry (18)',
            'tab_connectivity': '📶 Connectivity (9)',
            'tab_messaging': '📨 Messaging (2)',
            'optical_title': 'Optical Sensor Readings',
            'temp_title': 'Temperature Sensor Readings',
            'battery_title': 'Battery Sensor Readings',
            'snr_title': 'Signal-to-Noise Ratio (SNR)',
            'rsrp_title': 'Reference Signal Received Power (RSRP)',
            'rsrq_title': 'Reference Signal Received Quality (RSRQ)',
            'messaging_title': 'Messaging Statistics',
            'predict_button': '🔮 Predict Device Status',
            'predicting': 'Analyzing device features...',
            'result_title': '📊 Prediction Result',
            'result_critical': '🚨 CRITICAL DEVICE DETECTED',
            'result_normal': '✅ NORMAL DEVICE',
            'probability_label': 'Critical Probability',
            'recommendation_title': '💡 Recommendations',
            'rec_critical_1': '🔴 **Immediate Action Required** - Schedule maintenance within 48 hours',
            'rec_critical_2': '🔍 Inspect battery voltage, temperature sensors, and connectivity metrics',
            'rec_critical_3': '📝 Document device history and compare with similar critical cases',
            'rec_critical_4': '⚙️ Consider proactive replacement if device shows multiple warning signs',
            'rec_normal_1': '✅ **Continue Normal Monitoring** - Device operating within expected parameters',
            'rec_normal_2': '📊 Schedule routine inspection according to standard maintenance calendar',
            'rec_normal_3': '📈 Monitor trends over time - watch for degradation patterns',
            'top_features_title': '🎯 Top Contributing Features',
            'top_features_help': 'Features most influential for this prediction (based on global importance)',
        },
        
        # Insights Page
        'insights': {
            'title': '📊 Model Insights & Performance',
            'subtitle': 'Explore model behavior, feature importance, and validation results.',
            'performance_title': '📈 Model Performance Metrics',
            'recall_label': 'Recall',
            'recall_help': '11/14 critical devices detected',
            'precision_label': 'Precision',
            'precision_help': '84.6% of critical predictions correct',
            'f1_label': 'F1-Score',
            'f1_help': 'Harmonic mean of precision and recall',
            'auc_label': 'ROC-AUC',
            'auc_help': 'Area under ROC curve',
            'business_title': '💼 Business Impact Metrics',
            'critical_detected': 'Critical Detected',
            'critical_detected_delta': 'coverage',
            'false_alarms': 'False Alarms',
            'false_alarms_delta': 'FP rate',
            'normal_correct': 'Normal Correctly ID\'d',
            'normal_correct_delta': 'specificity',
            'confusion_title': '🔢 Confusion Matrix',
            'confusion_text': """
            The confusion matrix shows model performance on the **test set** (237 devices, 14 critical):
            
            - **True Positives (TP):** {tp} critical devices correctly identified
            - **False Negatives (FN):** {fn} critical devices missed (risk: unplanned failure)
            - **False Positives (FP):** {fp} normal devices incorrectly flagged (cost: unnecessary maintenance)
            - **True Negatives (TN):** {tn} normal devices correctly identified
            """,
            'feature_importance_title': '🎯 Feature Importance - Top 15',
            'feature_importance_text': """
            Feature importance reveals which telemetry signals drive predictions:
            
            **Key Insights:**
            - **Battery metrics** dominate (voltage stability critical for device health)
            - **Connectivity features** (SNR, RSRP, RSRQ) indicate communication stress
            - **Temperature patterns** show thermal management issues
            - **Optical sensor variability** captures environmental challenges
            """,
            'hyperparameters_title': '⚙️ Model Configuration',
            'hyperparameters_algorithm': 'Algorithm',
            'hyperparameters_iterations': 'Iterations',
            'hyperparameters_depth': 'Max Depth',
            'hyperparameters_learning_rate': 'Learning Rate',
            'hyperparameters_l2': 'L2 Regularization',
            'methodology_title': '🧪 Validation Methodology',
            'methodology_text': """
            **Data Split Strategy:**
            - **Training Set:** 552 devices (70%) with SMOTE oversampling
            - **Test Set:** 237 devices (30%) - kept original imbalanced distribution
            
            **Why SMOTE?**
            Synthetic Minority Oversampling Technique balances the severe 16.8:1 imbalance 
            by generating realistic synthetic critical device samples
            
            **Data Leakage Prevention:**
            Rigorous 7-step validation framework ensures no test data contamination
            
            **Cross-Validation:**
            5-fold stratified CV on training set confirmed stable performance
            """,
            'comparison_title': '📈 Algorithm Comparison',
            'comparison_text': """
            Evaluated three gradient boosting algorithms on identical data:
            
            | Algorithm | Recall | Precision | F1-Score | ROC-AUC |
            |-----------|--------|-----------|----------|---------|
            | **CatBoost** | **78.6%** | **84.6%** | **81.5%** | **0.862** |
            | XGBoost | 71.4% | 76.9% | 74.1% | 0.834 |
            | LightGBM | 64.3% | 81.8% | 72.0% | 0.818 |
            
            **CatBoost advantages:**
            - Ordered boosting reduces overfitting
            - Native categorical feature handling
            - Better calibrated probabilities for imbalanced data
            """,
        },
        
        # Research Context Page
        'research': {
            'title': '📖 Research Context & Methodology',
            'subtitle': 'Understanding the IoT Predictive Maintenance Problem',
            'model_version_info': '📊 **Current Model:** v2.0 FIELD-only (November 13, 2025) | This page documents the complete research journey from v1 to v2',
            'problem_title': '🔧 The Business Problem',
            'problem_content': """**IoT Device Failures in Production Environments**

Our organization deployed **789 IoT devices** for critical monitoring applications. 
Over time, **45 devices (5.7%) exhibited critical failures** requiring emergency maintenance.

**Challenges:**
- 🚨 **Unplanned downtime** causes revenue loss and customer dissatisfaction
- ⚙️ **Emergency repairs** cost 3-5x more than preventive maintenance
- � **No early warning system** - failures discovered reactively
- 🔍 **Manual inspection** of 789 devices infeasible (resource constraints)

**Business Objective:**
Build a machine learning model to **predict critical devices BEFORE failure** 
enabling **preventive maintenance** and **resource optimization**.""",
            'evolution_box_title': '**Model Evolution**',
            'evolution_v1_title': '**v1 (Mixed Data):**',
            'evolution_v1_devices': '789 devices (FACTORY+FIELD)',
            'evolution_v1_perf': 'Recall 78.6%, Precision 84.6%',
            'evolution_v1_auc': 'AUC 0.8621',
            'evolution_v1_issue': '⚠️ Lifecycle contamination',
            'evolution_v2_title': '**v2 (FIELD-only):**',
            'evolution_v2_devices': '762 devices (clean production)',
            'evolution_v2_perf': 'Recall 57.1%, Precision 57.1%',
            'evolution_v2_auc': '**AUC 0.9186** (+6.6%)',
            'evolution_v2_benefit': '✅ Better calibration',
            'technical_title': '� Technical Approach & Model Evolution',
            'technical_intro': 'Our solution evolved through **two major versions**, learning critical lessons about data quality and lifecycle contamination.',
            'tab_v1': '📦 v1: Mixed FACTORY+FIELD (Nov 2025)',
            'tab_v2': '✨ v2: FIELD-only Clean Data (Nov 13, 2025)',
        },
    },
    
    'pt-br': {
        # Common strings
        'common': {
            'language': 'Idioma',
            'english': 'English',
            'portuguese': 'Português (BR)',
            'success': 'Sucesso',
            'error': 'Erro',
            'warning': 'Aviso',
            'loading': 'Carregando',
            'download': 'Baixar',
            'upload': 'Enviar',
            'prediction': 'Predição',
            'results': 'Resultados',
            'features': 'Características',
            'required': 'Obrigatório',
            'optional': 'Opcional',
            'missing': 'Ausente',
            'devices': 'Dispositivos',
            'device': 'Dispositivo',
        },
        
        # Sidebar
        'sidebar': {
            'title': '🔧 Predição Dispositivos IoT',
            'model_version': 'Versão do Modelo',
            'training_date': 'Data Treinamento',
            'algorithm': 'Algoritmo',
            'recall': 'Recall',
            'precision': 'Precisão',
            'f1_score': 'F1-Score',
            'recall_delta': 'vs baseline',
            'precision_delta': 'vs meta',
        },
        
        # Home Page
        'home': {
            'title': '🏠 Predição de Dispositivos IoT Críticos',
            'subtitle': 'Modelo de Machine Learning para Manutenção Preventiva',
            'performance_title': '📈 Destaques de Performance do Modelo',
            'recall_label': 'Recall',
            'recall_help': 'Percentual de dispositivos críticos corretamente detectados (11/14)',
            'precision_label': 'Precisão',
            'precision_help': 'Acurácia das predições críticas (apenas 2 falsos alarmes)',
            'f1_label': 'F1-Score',
            'f1_help': 'Medida balanceada de precisão e recall',
            'auc_label': 'ROC-AUC',
            'auc_help': 'Área sob curva ROC - poder discriminativo geral do modelo',
            'objective_title': '🎯 Objetivo do Projeto',
            'objective_text': """
            Prever **dispositivos IoT críticos** antes da falha para habilitar **manutenção preventiva** 
            e evitar paradas não planejadas. O modelo analisa **29 características de telemetria** de 
            **789 dispositivos implantados** para identificar os **5.7%** em risco de falha crítica.
            """,
            'why_title': '💡 Por Que Isso Importa',
            'why_unplanned': '**Paradas não planejadas** custam 3-5x mais que manutenção preventiva',
            'why_emergency': '**Reparos emergenciais** interrompem operações e satisfação do cliente',
            'why_early': '**Detecção precoce** permite manutenção agendada em janelas ideais',
            'why_resource': '**Otimização de recursos** - foco em dispositivos de alto risco',
            'approach_title': '🔬 Abordagem Técnica',
            'approach_text': """
            **Algoritmo:** CatBoost com oversampling SMOTE
            
            **Desafio:** Desbalanceamento severo (razão 16.8:1 - apenas 45 críticos em 789 dispositivos)
            
            **Solução:** Balanceamento estratégico com SMOTE prevenindo vazamento de dados
            
            **Descoberta Chave:** Ordered boosting do CatBoost + features categóricas superaram 
            XGBoost e LightGBM para estes dados desbalanceados de telemetria
            """,
            'results_title': '📊 Resultados Principais',
            'results_recall': '**78.6% Recall** - 11 de 14 dispositivos críticos detectados no conjunto de teste',
            'results_precision': '**84.6% Precisão** - Apenas 2 falsos alarmes (overhead gerenciável)',
            'results_target': '**Supera meta de 80%** - Precisão excede requisito de negócio',
            'results_f1': '**81.5% F1-Score** - Performance balanceada forte',
            'deployment_title': '🚀 Pronto para Produção',
            'deployment_text': """
            O modelo está **pronto para produção** e disponível através desta interface web:
            
            - **Upload em Lote**: Processe múltiplos dispositivos via CSV
            - **Predição Individual**: Avaliação interativa para dispositivos únicos
            - **Insights do Modelo**: Explore métricas de performance e importância de features
            - **Contexto de Pesquisa**: Entenda a metodologia e descobertas
            """,
            'nav_title': '📍 Navegação Rápida',
            'nav_batch': '**Upload em Lote** - Envie CSV com múltiplos dispositivos',
            'nav_single': '**Predição Individual** - Insira características manualmente para um dispositivo',
            'nav_insights': '**Insights do Modelo** - Explore matriz de confusão e importância de features',
            'nav_research': '**Contexto de Pesquisa** - Aprenda sobre o problema e abordagem',
        },
        
        # Batch Upload Page
        'batch': {
            'title': '📤 Upload em Lote - Predição em Massa',
            'subtitle': 'Envie um arquivo CSV com características de dispositivos para obter predições de múltiplos dispositivos de uma vez.',
            'requirements_title': '📋 Requisitos de Formato CSV',
            'requirements_intro': 'Seu CSV deve conter **29 características obrigatórias**:',
            'requirements_telemetry': 'Características de Telemetria (18)',
            'requirements_telemetry_optical': '`optical_*`: mean, std, min, max, readings, below_threshold, range',
            'requirements_telemetry_temp': '`temp_*`: mean, std, min, max, above_threshold, range',
            'requirements_telemetry_battery': '`battery_*`: mean, std, min, max, below_threshold',
            'requirements_connectivity': 'Características de Conectividade (9)',
            'requirements_connectivity_snr': '`snr_*`: mean, std, min',
            'requirements_connectivity_rsrp': '`rsrp_*`: mean, std, min',
            'requirements_connectivity_rsrq': '`rsrq_*`: mean, std, min',
            'requirements_messaging': 'Características de Mensagens (2)',
            'requirements_messaging_list': '`total_messages`, `max_frame_count`',
            'requirements_optional': '**Colunas opcionais:** `device_id` (para identificação, não usado na predição)',
            'requirements_missing': '**Valores ausentes:** OK - modelo tem imputação integrada (estratégia mediana)',
            'template_button': '📥 Baixar Template CSV de Exemplo',
            'template_download': '💾 Baixar template.csv',
            'upload_label': 'Envie seu arquivo CSV',
            'upload_help': 'CSV com características de dispositivos (uma linha por dispositivo)',
            'loaded_success': '✅ Carregados {count} dispositivos do CSV',
            'preview_title': '👀 Pré-visualização dos Dados (primeiras 5 linhas)',
            'validation_error': '❌ Não é possível prosseguir - {count} características obrigatórias ausentes',
            'predict_button': '🚀 Gerar Predições',
            'predicting': '🔄 Gerando predições para {count} dispositivos...',
            'complete_success': '✅ Predições completas!',
            'summary_title': '📊 Resumo de Predições',
            'summary_total': 'Total de Dispositivos Analisados',
            'summary_critical': 'Previstos como Críticos',
            'summary_normal': 'Previstos como Normais',
            'summary_critical_pct': '{pct}% taxa crítica',
            'results_title': '📋 Resultados Detalhados',
            'results_help': 'Ordene por probabilidade para ver dispositivos de maior risco primeiro',
            'download_button': '💾 Baixar CSV de Resultados',
            'download_filename': 'resultados_predicoes.csv',
            'column_device_id': 'device_id',
            'column_prediction': 'predicao',
            'column_probability': 'probabilidade_critica',
            'column_risk_level': 'nivel_risco',
            'prediction_critical': 'CRÍTICO',
            'prediction_normal': 'NORMAL',
            'risk_high': 'ALTO',
            'risk_medium': 'MÉDIO',
            'risk_low': 'BAIXO',
        },
        
        # Single Prediction Page
        'single': {
            'title': '🔍 Predição Individual de Dispositivo',
            'subtitle': 'Insira características de um único dispositivo para obter avaliação instantânea de risco e recomendações.',
            'form_title': '📝 Entrada de Características do Dispositivo',
            'tab_telemetry': '📡 Telemetria (18)',
            'tab_connectivity': '📶 Conectividade (9)',
            'tab_messaging': '📨 Mensagens (2)',
            'optical_title': 'Leituras Sensor Óptico',
            'temp_title': 'Leituras Sensor de Temperatura',
            'battery_title': 'Leituras Sensor de Bateria',
            'snr_title': 'Relação Sinal-Ruído (SNR)',
            'rsrp_title': 'Potência Recebida Sinal Referência (RSRP)',
            'rsrq_title': 'Qualidade Recebida Sinal Referência (RSRQ)',
            'messaging_title': 'Estatísticas de Mensagens',
            'predict_button': '🔮 Prever Status do Dispositivo',
            'predicting': 'Analisando características do dispositivo...',
            'result_title': '📊 Resultado da Predição',
            'result_critical': '🚨 DISPOSITIVO CRÍTICO DETECTADO',
            'result_normal': '✅ DISPOSITIVO NORMAL',
            'probability_label': 'Probabilidade Crítica',
            'recommendation_title': '💡 Recomendações',
            'rec_critical_1': '🔴 **Ação Imediata Necessária** - Agende manutenção dentro de 48 horas',
            'rec_critical_2': '🔍 Inspecione voltagem bateria, sensores temperatura e métricas conectividade',
            'rec_critical_3': '📝 Documente histórico do dispositivo e compare com casos críticos similares',
            'rec_critical_4': '⚙️ Considere substituição proativa se dispositivo mostrar múltiplos sinais de alerta',
            'rec_normal_1': '✅ **Continue Monitoramento Normal** - Dispositivo operando dentro de parâmetros esperados',
            'rec_normal_2': '📊 Agende inspeção de rotina conforme calendário padrão de manutenção',
            'rec_normal_3': '📈 Monitore tendências ao longo do tempo - observe padrões de degradação',
            'top_features_title': '🎯 Características Principais Contribuintes',
            'top_features_help': 'Características mais influentes para esta predição (baseado em importância global)',
        },
        
        # Insights Page
        'insights': {
            'title': '📊 Insights e Performance do Modelo',
            'subtitle': 'Explore comportamento do modelo, importância de características e resultados de validação.',
            'performance_title': '📈 Métricas de Performance do Modelo',
            'recall_label': 'Recall',
            'recall_help': '11/14 dispositivos críticos detectados',
            'precision_label': 'Precisão',
            'precision_help': '84.6% das predições críticas corretas',
            'f1_label': 'F1-Score',
            'f1_help': 'Média harmônica de precisão e recall',
            'auc_label': 'ROC-AUC',
            'auc_help': 'Área sob curva ROC',
            'business_title': '💼 Métricas de Impacto de Negócio',
            'critical_detected': 'Críticos Detectados',
            'critical_detected_delta': 'cobertura',
            'false_alarms': 'Falsos Alarmes',
            'false_alarms_delta': 'taxa FP',
            'normal_correct': 'Normais Corretamente ID',
            'normal_correct_delta': 'especificidade',
            'confusion_title': '🔢 Matriz de Confusão',
            'confusion_text': """
            A matriz de confusão mostra performance do modelo no **conjunto de teste** (237 dispositivos, 14 críticos):
            
            - **Verdadeiros Positivos (TP):** {tp} dispositivos críticos corretamente identificados
            - **Falsos Negativos (FN):** {fn} dispositivos críticos perdidos (risco: falha não planejada)
            - **Falsos Positivos (FP):** {fp} dispositivos normais incorretamente sinalizados (custo: manutenção desnecessária)
            - **Verdadeiros Negativos (TN):** {tn} dispositivos normais corretamente identificados
            """,
            'feature_importance_title': '🎯 Importância de Características - Top 15',
            'feature_importance_text': """
            Importância de características revela quais sinais de telemetria direcionam predições:
            
            **Insights Principais:**
            - **Métricas de bateria** dominam (estabilidade voltagem crítica para saúde dispositivo)
            - **Características conectividade** (SNR, RSRP, RSRQ) indicam estresse comunicação
            - **Padrões temperatura** mostram problemas gestão térmica
            - **Variabilidade sensor óptico** captura desafios ambientais
            """,
            'hyperparameters_title': '⚙️ Configuração do Modelo',
            'hyperparameters_algorithm': 'Algoritmo',
            'hyperparameters_iterations': 'Iterações',
            'hyperparameters_depth': 'Profundidade Máxima',
            'hyperparameters_learning_rate': 'Taxa de Aprendizado',
            'hyperparameters_l2': 'Regularização L2',
            'methodology_title': '🧪 Metodologia de Validação',
            'methodology_text': """
            **Estratégia de Divisão de Dados:**
            - **Conjunto Treino:** 552 dispositivos (70%) com oversampling SMOTE
            - **Conjunto Teste:** 237 dispositivos (30%) - mantida distribuição desbalanceada original
            
            **Por Que SMOTE?**
            Synthetic Minority Oversampling Technique balanceia o severo desbalanceamento 16.8:1 
            gerando amostras sintéticas realistas de dispositivos críticos
            
            **Prevenção de Vazamento de Dados:**
            Framework rigoroso de validação em 7 etapas garante nenhuma contaminação de dados de teste
            
            **Validação Cruzada:**
            CV estratificado 5-fold no conjunto treino confirmou performance estável
            """,
            'comparison_title': '📈 Comparação de Algoritmos',
            'comparison_text': """
            Avaliados três algoritmos gradient boosting em dados idênticos:
            
            | Algoritmo | Recall | Precisão | F1-Score | ROC-AUC |
            |-----------|--------|----------|----------|---------|
            | **CatBoost** | **78.6%** | **84.6%** | **81.5%** | **0.862** |
            | XGBoost | 71.4% | 76.9% | 74.1% | 0.834 |
            | LightGBM | 64.3% | 81.8% | 72.0% | 0.818 |
            
            **Vantagens CatBoost:**
            - Ordered boosting reduz overfitting
            - Tratamento nativo de características categóricas
            - Melhores probabilidades calibradas para dados desbalanceados
            """,
        },
        
        # Research Context Page
        'research': {
            'title': '📖 Contexto de Pesquisa & Metodologia',
            'subtitle': 'Entendendo o Problema de Manutenção Preditiva IoT',
            'model_version_info': '📊 **Modelo Atual:** v2.0 FIELD-only (13 de novembro de 2025) | Esta página documenta a jornada completa de pesquisa do v1 ao v2',
            'problem_title': '🔧 O Problema de Negócio',
            'problem_content': """**Falhas de Dispositivos IoT em Ambientes de Produção**

Nossa organização implantou **789 dispositivos IoT** para aplicações críticas de monitoramento. 
Ao longo do tempo, **45 dispositivos (5.7%) apresentaram falhas críticas** exigindo manutenção emergencial.

**Desafios:**
- 🚨 **Tempo de inatividade não planejado** causa perda de receita e insatisfação do cliente
- ⚙️ **Reparos emergenciais** custam 3-5x mais que manutenção preventiva
- 📊 **Sem sistema de alerta precoce** - falhas descobertas reativamente
- 🔍 **Inspeção manual** de 789 dispositivos inviável (restrições de recursos)

**Objetivo de Negócio:**
Construir um modelo de machine learning para **prever dispositivos críticos ANTES da falha** 
habilitando **manutenção preventiva** e **otimização de recursos**.""",
            'evolution_box_title': '**Evolução do Modelo**',
            'evolution_v1_title': '**v1 (Dados Mistos):**',
            'evolution_v1_devices': '789 dispositivos (FACTORY+FIELD)',
            'evolution_v1_perf': 'Recall 78.6%, Precisão 84.6%',
            'evolution_v1_auc': 'AUC 0.8621',
            'evolution_v1_issue': '⚠️ Contaminação de ciclo de vida',
            'evolution_v2_title': '**v2 (FIELD-only):**',
            'evolution_v2_devices': '762 dispositivos (produção limpa)',
            'evolution_v2_perf': 'Recall 57.1%, Precisão 57.1%',
            'evolution_v2_auc': '**AUC 0.9186** (+6.6%)',
            'evolution_v2_benefit': '✅ Melhor calibração',
            'technical_title': '🔬 Abordagem Técnica & Evolução do Modelo',
            'technical_intro': 'Nossa solução evoluiu através de **duas versões principais**, aprendendo lições críticas sobre qualidade de dados e contaminação de ciclo de vida.',
            'tab_v1': '📦 v1: FACTORY+FIELD Mistos (Nov 2025)',
            'tab_v2': '✨ v2: Dados Limpos FIELD-only (13 Nov 2025)',
        },
    }
}


def get_text(section: str, key: str, lang: str = 'en') -> str:
    """
    Get translated text for a specific key
    
    Args:
        section: Section name (common, sidebar, home, batch, single, insights, research)
        key: Key name within section
        lang: Language code ('en' or 'pt-br')
    
    Returns:
        Translated string, fallback to English if not found
    """
    try:
        return TRANSLATIONS[lang][section][key]
    except KeyError:
        # Fallback to English if translation not found
        try:
            return TRANSLATIONS['en'][section][key]
        except KeyError:
            return f"[Missing: {section}.{key}]"


def get_language_from_session(st_session_state) -> str:
    """
    Get language code from Streamlit session state
    
    Args:
        st_session_state: Streamlit session state object
    
    Returns:
        Language code ('en' or 'pt-br')
    """
    language_display = st_session_state.get('language', 'English')
    return 'pt-br' if language_display == 'Português (BR)' else 'en'
