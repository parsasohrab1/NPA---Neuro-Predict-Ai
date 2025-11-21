"""
Integration tests for training pipeline
Tests data loading, preprocessing, training, and model registry
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock

try:
    import torch
    from torch.utils.data import DataLoader as TorchDataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

pytestmark = pytest.mark.skipif(not TORCH_AVAILABLE, reason="PyTorch not available")

from app.services.training import DataLoader, ModelTrainer, ModelEvaluator, ModelRegistry
from app.services.ai_model_service import MultiModalNeuralNetwork


@pytest.fixture
def synthetic_dataframe():
    """Generate synthetic DataFrame for testing"""
    np.random.seed(42)
    
    n_samples = 100
    data = []
    
    for i in range(n_samples):
        # Create mix of diagnoses
        diagnosis_prob = np.random.random()
        if diagnosis_prob < 0.3:
            diagnosis = 'Alzheimer'
            mmse = np.random.normal(20, 4)
            amyloid_beta = np.random.normal(650, 100)
        elif diagnosis_prob < 0.5:
            diagnosis = 'Parkinson'
            mmse = np.random.normal(26, 3)
            amyloid_beta = np.random.normal(550, 80)
        else:
            diagnosis = 'Normal'
            mmse = np.random.normal(28, 2)
            amyloid_beta = np.random.normal(500, 80)
        
        mmse = max(0, min(30, mmse))
        amyloid_beta = max(200, min(1000, amyloid_beta))
        
        data.append({
            'age': np.random.normal(70, 10),
            'gender': np.random.choice(['Male', 'Female']),
            'education_years': np.random.choice([12, 14, 16]),
            'mmse_score': mmse,
            'moca_score': mmse - 2,
            'memory_score': np.random.normal(50, 15),
            'attention_score': np.random.normal(55, 12),
            'executive_function_score': np.random.normal(52, 12),
            'amyloid_beta': amyloid_beta,
            'tau_protein': np.random.normal(200, 60),
            'dopamine_level': np.random.normal(90, 20),
            'apoe_e4_status': np.random.choice([0, 1]),
            'hippocampal_volume': np.random.normal(3200, 600),
            'cortical_thickness': np.random.normal(2.3, 0.3),
            'ventricular_volume': np.random.normal(35000, 8000),
            'white_matter_hyperintensities': np.random.exponential(2),
            'brain_volume_total': np.random.normal(1200000, 100000),
            'diagnosis': diagnosis
        })
    
    return pd.DataFrame(data)


class TestDataLoader:
    """Test data loading and preprocessing"""
    
    def test_preprocess_data(self, synthetic_dataframe):
        """Test data preprocessing"""
        data_loader = DataLoader()
        
        features, alzheimer_labels, parkinson_labels = data_loader.preprocess_data(synthetic_dataframe)
        
        assert features.shape[0] == len(synthetic_dataframe)
        assert features.shape[1] == 50  # 50 features
        assert len(alzheimer_labels) == len(synthetic_dataframe)
        assert len(parkinson_labels) == len(synthetic_dataframe)
        
        # Check label encoding
        assert np.all((alzheimer_labels == 0) | (alzheimer_labels == 1))
        assert np.all((parkinson_labels == 0) | (parkinson_labels == 1))
    
    def test_split_data(self, synthetic_dataframe):
        """Test data splitting"""
        data_loader = DataLoader()
        features, alzheimer_labels, parkinson_labels = data_loader.preprocess_data(synthetic_dataframe)
        
        data_splits = data_loader.split_data(
            features, alzheimer_labels, parkinson_labels,
            train_ratio=0.7, val_ratio=0.15, test_ratio=0.15
        )
        
        assert 'train' in data_splits
        assert 'val' in data_splits
        assert 'test' in data_splits
        assert 'scaler' in data_splits
        
        train_size = len(data_splits['train']['features'])
        val_size = len(data_splits['val']['features'])
        test_size = len(data_splits['test']['features'])
        total_size = train_size + val_size + test_size
        
        assert abs(total_size - len(synthetic_dataframe)) <= 1  # Allow for rounding
        
        # Check ratios are approximately correct
        assert abs(train_size / total_size - 0.7) < 0.1
        assert abs(val_size / total_size - 0.15) < 0.1
        assert abs(test_size / total_size - 0.15) < 0.1
    
    def test_create_dataloaders(self, synthetic_dataframe):
        """Test PyTorch DataLoader creation"""
        data_loader = DataLoader()
        features, alzheimer_labels, parkinson_labels = data_loader.preprocess_data(synthetic_dataframe)
        
        data_splits = data_loader.split_data(
            features, alzheimer_labels, parkinson_labels,
            train_ratio=0.7, val_ratio=0.15, test_ratio=0.15
        )
        
        dataloaders = data_loader.create_dataloaders(data_splits, batch_size=16)
        
        assert 'train' in dataloaders
        assert 'val' in dataloaders
        assert 'test' in dataloaders
        
        # Test that dataloaders can iterate
        batch = next(iter(dataloaders['train']))
        assert 'features' in batch
        assert 'alzheimer_label' in batch
        assert 'parkinson_label' in batch
        assert batch['features'].shape[0] <= 16  # Batch size


class TestModelTrainer:
    """Test model training"""
    
    @pytest.fixture
    def model_and_data(self, synthetic_dataframe):
        """Setup model and data for training tests"""
        device = torch.device("cpu")
        model = MultiModalNeuralNetwork(input_dim=50)
        model.to(device)
        
        data_loader = DataLoader()
        features, alzheimer_labels, parkinson_labels = data_loader.preprocess_data(synthetic_dataframe)
        data_splits = data_loader.split_data(
            features, alzheimer_labels, parkinson_labels,
            train_ratio=0.7, val_ratio=0.15, test_ratio=0.15
        )
        dataloaders = data_loader.create_dataloaders(data_splits, batch_size=16)
        
        return model, device, dataloaders
    
    def test_train_epoch(self, model_and_data, tmp_path):
        """Test training one epoch"""
        model, device, dataloaders = model_and_data
        
        trainer = ModelTrainer(model, device, model_dir=tmp_path)
        
        import torch.nn as nn
        import torch.optim as optim
        
        criterion = nn.BCELoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        
        metrics = trainer.train_epoch(dataloaders['train'], optimizer, criterion)
        
        assert 'loss' in metrics
        assert 'alzheimer_accuracy' in metrics
        assert 'parkinson_accuracy' in metrics
        assert 0.0 <= metrics['loss'] < 10.0  # Reasonable loss range
        assert 0.0 <= metrics['alzheimer_accuracy'] <= 1.0
        assert 0.0 <= metrics['parkinson_accuracy'] <= 1.0
    
    def test_validate(self, model_and_data, tmp_path):
        """Test validation"""
        model, device, dataloaders = model_and_data
        
        trainer = ModelTrainer(model, device, model_dir=tmp_path)
        
        import torch.nn as nn
        criterion = nn.BCELoss()
        
        metrics = trainer.validate(dataloaders['val'], criterion)
        
        assert 'loss' in metrics
        assert 'alzheimer_accuracy' in metrics
        assert 'parkinson_accuracy' in metrics
        assert 0.0 <= metrics['loss'] < 10.0
        assert 0.0 <= metrics['alzheimer_accuracy'] <= 1.0
        assert 0.0 <= metrics['parkinson_accuracy'] <= 1.0
    
    def test_train_full(self, model_and_data, tmp_path):
        """Test full training with early stopping"""
        model, device, dataloaders = model_and_data
        
        trainer = ModelTrainer(model, device, model_dir=tmp_path)
        
        results = trainer.train(
            dataloaders['train'],
            dataloaders['val'],
            epochs=5,  # Short training for test
            learning_rate=0.001,
            patience=3
        )
        
        assert 'training_history' in results
        assert 'best_model_path' in results
        assert 'best_val_loss' in results
        
        assert len(results['training_history']['train_loss']) > 0
        assert len(results['training_history']['val_loss']) > 0
        
        # Check that validation loss improved (or at least was tracked)
        assert results['best_val_loss'] < float('inf')


class TestModelEvaluator:
    """Test model evaluation"""
    
    @pytest.fixture
    def trained_model_and_data(self, synthetic_dataframe):
        """Setup trained model and data for evaluation"""
        device = torch.device("cpu")
        model = MultiModalNeuralNetwork(input_dim=50)
        model.to(device)
        
        data_loader = DataLoader()
        features, alzheimer_labels, parkinson_labels = data_loader.preprocess_data(synthetic_dataframe)
        data_splits = data_loader.split_data(
            features, alzheimer_labels, parkinson_labels,
            train_ratio=0.7, val_ratio=0.15, test_ratio=0.15
        )
        dataloaders = data_loader.create_dataloaders(data_splits, batch_size=16)
        
        # Quick training
        trainer = ModelTrainer(model, device)
        trainer.train(
            dataloaders['train'],
            dataloaders['val'],
            epochs=3,
            learning_rate=0.001,
            patience=2
        )
        
        return model, device, dataloaders
    
    def test_evaluate_model(self, trained_model_and_data):
        """Test model evaluation"""
        model, device, dataloaders = trained_model_and_data
        
        evaluator = ModelEvaluator()
        metrics = evaluator.evaluate_model(model, dataloaders['test'], device)
        
        assert 'alzheimer' in metrics
        assert 'parkinson' in metrics
        
        # Check Alzheimer's metrics
        alz_metrics = metrics['alzheimer']
        assert 'accuracy' in alz_metrics
        assert 'sensitivity' in alz_metrics
        assert 'specificity' in alz_metrics
        assert 'precision' in alz_metrics
        assert 'f1_score' in alz_metrics
        assert 'auc_roc' in alz_metrics
        
        assert 0.0 <= alz_metrics['accuracy'] <= 1.0
        assert 0.0 <= alz_metrics['sensitivity'] <= 1.0
        assert 0.0 <= alz_metrics['specificity'] <= 1.0
    
    def test_generate_clinical_report(self, trained_model_and_data):
        """Test clinical report generation"""
        model, device, dataloaders = trained_model_and_data
        
        evaluator = ModelEvaluator()
        metrics = evaluator.evaluate_model(model, dataloaders['test'], device)
        
        report = evaluator.generate_clinical_report(metrics)
        
        assert isinstance(report, str)
        assert len(report) > 0
        assert "CLINICAL VALIDATION REPORT" in report
        assert "ALZHEIMER" in report or "alzheimer" in report.lower()
        assert "PARKINSON" in report or "parkinson" in report.lower()


class TestModelRegistry:
    """Test model registry"""
    
    def test_registry_creation(self, tmp_path):
        """Test registry creation"""
        registry_path = tmp_path / "registry.json"
        registry = ModelRegistry(registry_path)
        
        assert registry.registry_path == registry_path
        assert 'models' in registry.registry
        assert 'current_model' in registry.registry
    
    def test_register_model(self, tmp_path):
        """Test model registration"""
        registry = ModelRegistry(tmp_path / "registry.json")
        
        # Create dummy model file
        model_path = tmp_path / "model.pth"
        torch.save({}, model_path)  # Save empty dict as placeholder
        
        metrics = {
            'training': {'best_val_loss': 0.5},
            'test': {'alzheimer': {'accuracy': 0.85}}
        }
        
        version = registry.register_model(
            model_path,
            metrics,
            version="test_v1.0",
            description="Test model"
        )
        
        assert version == "test_v1.0"
        assert len(registry.list_models()) == 1
        
        model_entry = registry.get_model(version)
        assert model_entry is not None
        assert model_entry['version'] == version
        assert model_entry['description'] == "Test model"
    
    def test_set_active_model(self, tmp_path):
        """Test setting active model"""
        registry = ModelRegistry(tmp_path / "registry.json")
        
        model_path1 = tmp_path / "model1.pth"
        model_path2 = tmp_path / "model2.pth"
        torch.save({}, model_path1)
        torch.save({}, model_path2)
        
        v1 = registry.register_model(model_path1, {'test': {}}, version="v1")
        v2 = registry.register_model(model_path2, {'test': {}}, version="v2")
        
        assert registry.set_active_model(v1) is True
        active = registry.get_active_model()
        assert active is not None
        assert active['version'] == v1
        
        assert registry.set_active_model(v2) is True
        active = registry.get_active_model()
        assert active is not None
        assert active['version'] == v2


class TestFullTrainingPipeline:
    """Integration test for complete training pipeline"""
    
    def test_full_pipeline(self, synthetic_dataframe, tmp_path):
        """Test complete training pipeline from data to registered model"""
        # Load and preprocess data
        data_loader = DataLoader()
        features, alzheimer_labels, parkinson_labels = data_loader.preprocess_data(synthetic_dataframe)
        
        # Split data
        data_splits = data_loader.split_data(
            features, alzheimer_labels, parkinson_labels,
            train_ratio=0.7, val_ratio=0.15, test_ratio=0.15
        )
        
        # Create dataloaders
        dataloaders = data_loader.create_dataloaders(data_splits, batch_size=16)
        
        # Initialize and train model
        device = torch.device("cpu")
        model = MultiModalNeuralNetwork(input_dim=50)
        model.to(device)
        
        trainer = ModelTrainer(model, device, model_dir=tmp_path)
        training_results = trainer.train(
            dataloaders['train'],
            dataloaders['val'],
            epochs=5,
            learning_rate=0.001,
            patience=3
        )
        
        assert training_results['best_model_path'] is not None
        assert Path(training_results['best_model_path']).exists()
        
        # Load best model
        model.load_state_dict(torch.load(training_results['best_model_path'], map_location=device))
        
        # Evaluate model
        evaluator = ModelEvaluator()
        test_metrics = evaluator.evaluate_model(model, dataloaders['test'], device)
        
        assert 'alzheimer' in test_metrics
        assert 'parkinson' in test_metrics
        
        # Register model
        registry = ModelRegistry(tmp_path / "registry.json")
        version = registry.register_model(
            Path(training_results['best_model_path']),
            {
                'training': {'best_val_loss': training_results['best_val_loss']},
                'test': test_metrics
            },
            version="test_pipeline_v1"
        )
        
        assert version == "test_pipeline_v1"
        registered_model = registry.get_model(version)
        assert registered_model is not None
        assert registered_model['metrics']['test']['alzheimer']['accuracy'] > 0

