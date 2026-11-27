"""Machine Learning Repository Analyzer.

Analyzes GitHub repositories using README documentation, repository tree structures,
and configuration files to evaluate ML frameworks, architectures, pipelines, and deployment.
Clearly separates verified/documented findings from unverified aspects.
"""

import re
from typing import Optional

from github_mcp.github_client import GitHubClient
from github_mcp.models import (
    AnalysisField,
    FrameworkItem,
    MLRepositoryAnalysis,
    RepositoryTree,
)

# Known ML framework definitions: (keyword, canonical_name, category)
ML_FRAMEWORK_CATALOG: list[tuple[str, str, str]] = [
    # Deep Learning Core
    ("torch", "PyTorch", "Deep Learning Core"),
    ("pytorch-lightning", "PyTorch Lightning", "Deep Learning Framework"),
    ("lightning", "PyTorch Lightning", "Deep Learning Framework"),
    ("tensorflow", "TensorFlow", "Deep Learning Core"),
    ("keras", "Keras", "Deep Learning Core"),
    ("jax", "JAX", "Deep Learning / Scientific Computing"),
    ("flax", "Flax", "Deep Learning Framework"),
    # Classical ML & Tabular
    ("scikit-learn", "Scikit-Learn", "Classical Machine Learning"),
    ("sklearn", "Scikit-Learn", "Classical Machine Learning"),
    ("xgboost", "XGBoost", "Gradient Boosting / Tabular ML"),
    ("lightgbm", "LightGBM", "Gradient Boosting / Tabular ML"),
    ("catboost", "CatBoost", "Gradient Boosting / Tabular ML"),
    ("statsmodels", "Statsmodels", "Statistical Modeling"),
    # NLP & LLM
    ("transformers", "Hugging Face Transformers", "NLP / Foundation Models"),
    ("diffusers", "Hugging Face Diffusers", "Diffusion Models / Generative AI"),
    ("datasets", "Hugging Face Datasets", "Data Management"),
    ("tokenizers", "Hugging Face Tokenizers", "NLP / Tokenization"),
    ("peft", "Hugging Face PEFT", "Parameter-Efficient Fine-Tuning"),
    ("trl", "Hugging Face TRL", "Reinforcement Learning from Human Feedback"),
    ("sentence-transformers", "Sentence Transformers", "Embeddings / Semantic Search"),
    ("langchain", "LangChain", "LLM Application Framework"),
    ("llama-index", "LlamaIndex", "LLM Data Framework"),
    ("spacy", "spaCy", "Natural Language Processing"),
    ("nltk", "NLTK", "Natural Language Processing"),
    ("vllm", "vLLM", "High-Throughput LLM Serving"),
    # Computer Vision
    ("opencv-python", "OpenCV", "Computer Vision"),
    ("cv2", "OpenCV", "Computer Vision"),
    ("albumentations", "Albumentations", "Computer Vision / Data Augmentation"),
    ("timm", "timm (PyTorch Image Models)", "Computer Vision / Model Zoo"),
    ("ultralytics", "Ultralytics YOLO", "Object Detection / Computer Vision"),
    ("detectron2", "Detectron2", "Object Detection / Segmentation"),
    ("torchvision", "TorchVision", "Computer Vision Core"),
    # MLOps & Experiment Tracking
    ("mlflow", "MLflow", "MLOps / Experiment Tracking"),
    ("wandb", "Weights & Biases (W&B)", "MLOps / Experiment Tracking"),
    ("tensorboard", "TensorBoard", "Experiment Visualization"),
    ("dvc", "Data Version Control (DVC)", "Data & Model Versioning"),
    ("clearml", "ClearML", "MLOps Orchestration"),
    ("hydra-core", "Hydra", "Configuration Management"),
    ("optuna", "Optuna", "Hyperparameter Optimization"),
    # Serving & Deployment
    ("fastapi", "FastAPI", "API / Web Serving"),
    ("flask", "Flask", "API / Web Serving"),
    ("streamlit", "Streamlit", "Interactive ML UI"),
    ("gradio", "Gradio", "Interactive ML Demo UI"),
    ("onnxruntime", "ONNX Runtime", "High-Performance Model Inference"),
    ("onnx", "ONNX", "Model Interoperability Format"),
    ("tritonclient", "NVIDIA Triton Inference Server Client", "High-Throughput Model Serving"),
    ("bentoml", "BentoML", "Model Packaging & Serving"),
    ("torchserve", "TorchServe", "PyTorch Model Serving"),
]

# Model architecture keywords to match in README and code
ARCHITECTURE_PATTERNS = [
    r"\b(transformer|transformers|vit|vision transformer)\b",
    r"\b(bert|roberta|deberta|distilbert|electra|t5|bart)\b",
    r"\b(gpt|llama|mistral|falcon|qwen|phi|claude|gemini)\b",
    r"\b(resnet|resnext|efficientnet|convnext|vgg|mobilenet|densenet)\b",
    r"\b(yolo|yolov[0-9]+|rcnn|faster-rcnn|mask-rcnn|retinanet|ssd)\b",
    r"\b(unet|u-net|deeplabv[0-9]+|segnet)\b",
    r"\b(diffusion|stable diffusion|ddpm|ddim|latent diffusion)\b",
    r"\b(random forest|gradient boosting|decision tree|logistic regression|svm|linear regression|knn|kmeans)\b",
    r"\b(cnn|rnn|lstm|gru|mlp|autoencoder|variational autoencoder|vae|gan)\b",
    r"\b(graph neural network|gnn|gcn|gat)\b",
]

# Evaluation metric patterns
METRIC_PATTERNS = [
    r"\b(accuracy|top-[0-9]+ accuracy)\b",
    r"\b(f1[- ]score|f1|macro f1|micro f1|weighted f1)\b",
    r"\b(precision|recall|specificity)\b",
    r"\b(roc[- ]auc|auroc|pr[- ]auc)\b",
    r"\b(map|map@[0-9]+|ap@[0-9]+|iou|dice score|dice coefficient)\b",
    r"\b(bleu|bleu-[0-9]+|rouge|rouge-[0-9]+|rouge-l|meteor|bertscore)\b",
    r"\b(perplexity|loss|cross[- ]entropy loss)\b",
    r"\b(mse|rmse|mae|r2|r-squared|mape)\b",
    r"\b(latency|throughput|fps|flops|parameters)\b",
]


class MLRepositoryAnalyzer:
    """Orchestrates comprehensive analysis of ML repositories from GitHub metadata."""

    def __init__(self, client: GitHubClient):
        self.client = client

    async def analyze(
        self,
        owner: str,
        repo: str,
        branch: Optional[str] = None,
    ) -> MLRepositoryAnalysis:
        """Run ML analysis by fetching tree, configuration files, and documentation."""
        # 1. Fetch file tree
        tree: RepositoryTree = await self.client.get_repository_tree(
            owner=owner, repo=repo, branch=branch, recursive=True
        )
        analyzed_branch = tree.branch

        # 2. Categorize repository files from tree
        tree_paths = [item.path for item in tree.items]
        readme_path = self._find_first_matching(
            tree_paths, [r"(?i)^readme(\.md|\.rst|\.txt|\.markdown)?$"]
        )
        dep_files = self._find_all_matching(
            tree_paths,
            [
                r"(?i)(^|/)requirements.*\.txt$",
                r"(?i)(^|/)environment\.ya?ml$",
                r"(?i)(^|/)pyproject\.toml$",
                r"(?i)(^|/)setup\.(py|cfg)$",
                r"(?i)(^|/)pipfile$",
            ],
        )
        ml_code_files = self._find_all_matching(
            tree_paths,
            [
                r"(?i)(^|/)(train|train_.*|trainer|pipeline|run)\.py$",
                r"(?i)(^|/)(model|models/.*|architecture|network|backbone)\.py$",
                r"(?i)(^|/)(eval|evaluate|metrics|test_eval|benchmark)\.py$",
                r"(?i)(^|/)(dataset|datasets/.*|dataloader|data_loader|preprocess)\.py$",
                r"(?i)\.ipynb$",
                r"(?i)(^|/)dockerfile$",
                r"(?i)(^|/)docker-compose\.ya?ml$",
                r"(?i)(^|/)(app|serve|main|api/.*)\.py$",
                r"(?i)\.(pt|pth|onnx|safetensors|h5|ckpt|joblib)$",
            ],
        )

        # 3. Read README content if present
        readme_text = ""
        if readme_path:
            try:
                readme_obj = await self.client.get_file_contents(
                    owner=owner, repo=repo, path=readme_path, branch=analyzed_branch
                )
                readme_text = readme_obj.content
            except Exception:
                readme_text = ""

        # 4. Read primary dependency file
        dep_texts: dict[str, str] = {}
        for dep_file in dep_files[:3]:  # Read top 3 dependency files
            try:
                dep_obj = await self.client.get_file_contents(
                    owner=owner, repo=repo, path=dep_file, branch=analyzed_branch
                )
                dep_texts[dep_file] = dep_obj.content
            except Exception:
                pass

        # 5. Detect ML frameworks and libraries
        detected_frameworks = self._detect_frameworks(dep_texts, readme_text)

        # 6. Analyze problem statement
        problem_statement = self._analyze_problem_statement(readme_text, readme_path)

        # 7. Analyze model architecture
        model_architecture = self._analyze_model_architecture(
            readme_text, tree_paths, ml_code_files
        )

        # 8. Analyze datasets
        datasets = self._analyze_datasets(readme_text, tree_paths)

        # 9. Analyze training pipeline
        training_pipeline = self._analyze_training_pipeline(readme_text, tree_paths, ml_code_files)

        # 10. Analyze evaluation metrics
        evaluation_metrics = self._analyze_evaluation_metrics(readme_text, ml_code_files)

        # 11. Analyze deployment approach
        deployment_approach = self._analyze_deployment(readme_text, tree_paths, detected_frameworks)

        # 12. Calculate ML confidence score
        ml_score, is_ml = self._calculate_ml_confidence(
            detected_frameworks, ml_code_files, readme_text, tree_paths
        )

        # 13. Formulate summary notes
        summary = self._generate_summary_notes(
            repo=f"{owner}/{repo}",
            is_ml=is_ml,
            frameworks=detected_frameworks,
            problem=problem_statement,
            architecture=model_architecture,
            datasets=datasets,
            pipeline=training_pipeline,
            eval_metrics=evaluation_metrics,
            deployment=deployment_approach,
        )

        return MLRepositoryAnalysis(
            repository=f"{owner}/{repo}",
            analyzed_branch=analyzed_branch,
            is_ml_project=is_ml,
            ml_confidence_score=round(ml_score, 2),
            problem_statement=problem_statement,
            frameworks=detected_frameworks,
            model_architecture=model_architecture,
            datasets=datasets,
            training_pipeline=training_pipeline,
            evaluation_metrics=evaluation_metrics,
            deployment_approach=deployment_approach,
            key_files_found=ml_code_files[:25],
            summary_notes=summary,
        )

    def _find_first_matching(self, paths: list[str], patterns: list[str]) -> Optional[str]:
        for p in paths:
            for pat in patterns:
                if re.search(pat, p):
                    return p
        return None

    def _find_all_matching(self, paths: list[str], patterns: list[str]) -> list[str]:
        matched = []
        for p in paths:
            for pat in patterns:
                if re.search(pat, p):
                    matched.append(p)
                    break
        return matched

    def _detect_frameworks(
        self, dep_texts: dict[str, str], readme_text: str
    ) -> list[FrameworkItem]:
        results: list[FrameworkItem] = []
        seen_names = set()

        combined_deps_lower = " \n".join(
            f"{path}:\n{content.lower()}" for path, content in dep_texts.items()
        )
        readme_lower = readme_text.lower()

        for kw, canonical_name, category in ML_FRAMEWORK_CATALOG:
            if canonical_name in seen_names:
                continue

            # Check in dependencies
            pattern_dep = rf"(?i)(?:^|[\s,;=\'\"]){re.escape(kw)}(?:[\s=><~;\:\'\"]|$)"
            in_deps = bool(re.search(pattern_dep, combined_deps_lower))

            # Find matching file evidence if in deps
            dep_evidence = ""
            if in_deps:
                for file_path, content in dep_texts.items():
                    for line in content.splitlines():
                        if re.search(pattern_dep, line.lower()):
                            dep_evidence = f"{file_path}: {line.strip()}"
                            break
                    if dep_evidence:
                        break

            # Check in readme
            pattern_readme = rf"(?i)\b{re.escape(kw)}\b"
            in_readme = bool(re.search(pattern_readme, readme_lower))

            if in_deps or in_readme:
                seen_names.add(canonical_name)
                evidence_text = dep_evidence or (
                    f"Mentioned in documentation: '{kw}'" if in_readme else ""
                )
                results.append(
                    FrameworkItem(
                        name=canonical_name,
                        category=category,
                        verified_in_dependencies=in_deps,
                        mentioned_in_readme=in_readme,
                        evidence=evidence_text,
                    )
                )

        return results

    def _analyze_problem_statement(
        self, readme_text: str, readme_path: Optional[str]
    ) -> AnalysisField:
        if not readme_text or not readme_path:
            return AnalysisField(
                status="unverified",
                details="No README documentation found in the repository to identify the problem statement.",
                evidence=[],
            )

        # Look for typical problem/intro/about sections in README
        sections = re.split(r"(?m)^#{1,3}\s+", readme_text)
        candidates = []

        for sec in sections:
            lines = sec.strip().splitlines()
            if not lines:
                continue
            header = lines[0].lower().strip()
            body = " ".join(lines[1:6]).strip()

            if any(
                term in header
                for term in [
                    "about",
                    "overview",
                    "introduction",
                    "problem",
                    "description",
                    "project",
                    "motivation",
                    "background",
                    "goal",
                    "objective",
                ]
            ):
                if len(body) > 20:
                    candidates.append((header, body[:300]))

        if candidates:
            header, excerpt = candidates[0]
            return AnalysisField(
                status="documented",
                details=f"Documented in README under '{header.title()}': {excerpt}",
                evidence=[f"{readme_path} (Section: {header})"],
            )

        # Fallback to first non-empty paragraph of README
        paragraphs = [p.strip() for p in readme_text.split("\n\n") if len(p.strip()) > 40]
        if paragraphs:
            first_p = paragraphs[0].replace("\n", " ")[:300]
            return AnalysisField(
                status="documented",
                details=f"Extracted from README introductory paragraph: {first_p}",
                evidence=[f"{readme_path} (Introductory section)"],
            )

        return AnalysisField(
            status="unverified",
            details="README exists but contains no clear problem statement or project description.",
            evidence=[readme_path],
        )

    def _analyze_model_architecture(
        self, readme_text: str, tree_paths: list[str], ml_code_files: list[str]
    ) -> AnalysisField:
        evidence = []
        found_architectures = []

        # 1. Search in README
        for pat in ARCHITECTURE_PATTERNS:
            matches = re.findall(pat, readme_text, re.IGNORECASE)
            for m in matches:
                item = m.strip().title()
                if item not in found_architectures:
                    found_architectures.append(item)
                    evidence.append(f"README mentions: '{m}'")

        # 2. Check architecture-related files in tree
        arch_files = [
            f
            for f in tree_paths
            if re.search(r"(?i)(model|architecture|network|backbone|resnet|bert|yolo|unet)", f)
        ]
        for af in arch_files[:5]:
            evidence.append(f"Tree structure contains model file: {af}")

        if found_architectures:
            details_str = (
                f"Identified model architecture components: {', '.join(found_architectures)}. "
                + (f"Verified with code files ({', '.join(arch_files[:3])})." if arch_files else "")
            )
            return AnalysisField(
                status="documented",
                details=details_str.strip(),
                evidence=evidence[:6],
            )
        elif arch_files:
            return AnalysisField(
                status="inferred",
                details=(
                    f"Model architecture source files detected in repository ({', '.join(arch_files[:4])}), "
                    "but specific architectural names/hyperparameters are not explicitly documented in README."
                ),
                evidence=evidence[:4],
            )

        return AnalysisField(
            status="unverified",
            details="No specific model architecture, neural network backbone, or ML model type could be verified from documentation or files.",
            evidence=[],
        )

    def _analyze_datasets(self, readme_text: str, tree_paths: list[str]) -> AnalysisField:
        evidence = []
        found_datasets = []

        # Search for dataset sections in README
        sections = re.split(r"(?m)^#{1,3}\s+", readme_text)
        for sec in sections:
            lines = sec.strip().splitlines()
            if not lines:
                continue
            header = lines[0].lower().strip()
            if any(term in header for term in ["dataset", "data", "benchmark", "corpus"]):
                body = " ".join(lines[1:5]).strip()[:300]
                if body:
                    found_datasets.append(f"Documented in '{header.title()}': {body}")
                    evidence.append(f"README section: #{header}")

        # Search for common dataset names in README
        known_datasets = [
            "ImageNet",
            "COCO",
            "MNIST",
            "CIFAR-10",
            "CIFAR-100",
            "SQuAD",
            "GLUE",
            "SuperGLUE",
            "Kaggle",
            "Common Voice",
            "LibriSpeech",
            "CelebA",
            "PASCAL VOC",
            "MIMIC",
        ]
        for ds in known_datasets:
            if re.search(rf"\b{re.escape(ds)}\b", readme_text, re.IGNORECASE):
                if not any(ds in fd for fd in found_datasets):
                    found_datasets.append(f"References benchmark dataset: {ds}")
                    evidence.append(f"README mentions {ds}")

        # Check data files in tree
        data_paths = [
            p
            for p in tree_paths
            if re.search(r"(?i)(^|/)(data/|datasets?/|data_loader|prepare_data|download_data)", p)
        ]
        for dp in data_paths[:4]:
            evidence.append(f"Data-related repository path: {dp}")

        if found_datasets:
            return AnalysisField(
                status="documented",
                details="; ".join(found_datasets[:3]),
                evidence=evidence[:6],
            )
        elif data_paths:
            return AnalysisField(
                status="inferred",
                details=(
                    f"Data loading or storage paths identified in repository structure ({', '.join(data_paths[:3])}), "
                    "but dataset origin and preparation are not explicitly documented in README."
                ),
                evidence=evidence[:4],
            )

        return AnalysisField(
            status="unverified",
            details="No dataset description, benchmark references, or data ingestion paths found in documentation or repository tree.",
            evidence=[],
        )

    def _analyze_training_pipeline(
        self, readme_text: str, tree_paths: list[str], ml_code_files: list[str]
    ) -> AnalysisField:
        evidence = []
        pipeline_details = []

        # Check training files
        train_scripts = [
            f for f in tree_paths if re.search(r"(?i)(train|trainer|pipeline|finetune|fit)\.py$", f)
        ]
        if train_scripts:
            pipeline_details.append(f"Training script(s) found: {', '.join(train_scripts)}")
            evidence.extend(train_scripts[:3])

        # Check experiment tracking tools in tree or readme
        tracking_tools = []
        for tool, pat in [
            ("MLflow", r"\bmlflow\b"),
            ("Weights & Biases", r"\bwandb\b"),
            ("TensorBoard", r"\btensorboard\b"),
            ("DVC", r"\bdvc\b"),
        ]:
            if re.search(pat, readme_text, re.IGNORECASE) or any(
                re.search(pat, p, re.IGNORECASE) for p in tree_paths
            ):
                tracking_tools.append(tool)

        if tracking_tools:
            pipeline_details.append(f"Experiment tracking: {', '.join(tracking_tools)}")
            evidence.append(f"Tracking tools: {', '.join(tracking_tools)}")

        # Search for training commands or hyperparameter descriptions in README
        train_cmds = re.findall(
            r"(?:python\s+(?:train|run)\.py[^\n`]+)", readme_text, re.IGNORECASE
        )
        if train_cmds:
            pipeline_details.append(f"Documented execution: '{train_cmds[0].strip()}'")
            evidence.append("README contains training run instructions")

        if pipeline_details:
            status = "documented" if train_cmds or tracking_tools else "inferred"
            return AnalysisField(
                status=status,
                details="; ".join(pipeline_details),
                evidence=evidence[:6],
            )

        return AnalysisField(
            status="unverified",
            details="No training pipeline, trainer scripts, or experiment tracking configs verified.",
            evidence=[],
        )

    def _analyze_evaluation_metrics(
        self, readme_text: str, ml_code_files: list[str]
    ) -> AnalysisField:
        evidence = []
        found_metrics = []

        for pat in METRIC_PATTERNS:
            matches = re.findall(pat, readme_text, re.IGNORECASE)
            for m in matches:
                clean_m = m.strip().upper() if len(m) <= 4 else m.strip().title()
                if clean_m not in found_metrics:
                    found_metrics.append(clean_m)
                    evidence.append(f"README metric reference: '{m}'")

        eval_scripts = [
            f for f in ml_code_files if re.search(r"(?i)(eval|evaluate|metrics|benchmark)", f)
        ]
        if eval_scripts:
            evidence.append(f"Evaluation source files: {', '.join(eval_scripts[:3])}")

        if found_metrics:
            return AnalysisField(
                status="documented",
                details=f"Documented evaluation metrics: {', '.join(found_metrics)}. "
                + (f"Evaluation code: {', '.join(eval_scripts[:2])}." if eval_scripts else ""),
                evidence=evidence[:6],
            )
        elif eval_scripts:
            return AnalysisField(
                status="inferred",
                details=f"Evaluation scripts present ({', '.join(eval_scripts)}), but numerical evaluation metrics or benchmark results are not documented in README.",
                evidence=evidence[:4],
            )

        return AnalysisField(
            status="unverified",
            details="No evaluation metrics, validation protocols, or benchmark results verified in documentation or code.",
            evidence=[],
        )

    def _analyze_deployment(
        self, readme_text: str, tree_paths: list[str], frameworks: list[FrameworkItem]
    ) -> AnalysisField:
        evidence = []
        deployment_clues = []

        # Check Docker / Containers
        docker_files = [
            p for p in tree_paths if re.search(r"(?i)(dockerfile|docker-compose\.ya?ml)", p)
        ]
        if docker_files:
            deployment_clues.append(f"Containerized ({', '.join(docker_files)})")
            evidence.extend(docker_files)

        # Check serving frameworks
        serving_fws = [
            f.name
            for f in frameworks
            if f.category
            in [
                "API / Web Serving",
                "Interactive ML UI",
                "Interactive ML Demo UI",
                "High-Throughput Model Serving",
                "Model Packaging & Serving",
            ]
        ]
        if serving_fws:
            deployment_clues.append(f"Serving framework: {', '.join(serving_fws)}")
            evidence.append(f"Serving frameworks in project: {', '.join(serving_fws)}")

        # Check app/serve files in tree
        app_files = [
            p for p in tree_paths if re.search(r"(?i)(^|/)(app|serve|main|api/.*)\.py$", p)
        ]
        if app_files:
            evidence.append(f"Entrypoint/API scripts: {', '.join(app_files[:3])}")

        # Check cloud/deployment mentions in README
        cloud_matches = re.findall(
            r"\b(docker|kubernetes|k8s|sagemaker|vertex ai|aws|azure|gcp|hugging\s*face\s*spaces)\b",
            readme_text,
            re.IGNORECASE,
        )
        if cloud_matches:
            unique_cloud = sorted(list(set(m.title() for m in cloud_matches)))
            deployment_clues.append(f"Infrastructure referenced: {', '.join(unique_cloud)}")
            evidence.append(f"Documentation mentions: {', '.join(unique_cloud)}")

        if deployment_clues:
            status = "documented" if (docker_files or serving_fws or cloud_matches) else "inferred"
            return AnalysisField(
                status=status,
                details="; ".join(deployment_clues),
                evidence=evidence[:6],
            )

        return AnalysisField(
            status="unverified",
            details="No deployment architecture, API endpoints, container configs, or web demos documented.",
            evidence=[],
        )

    def _calculate_ml_confidence(
        self,
        frameworks: list[FrameworkItem],
        ml_code_files: list[str],
        readme_text: str,
        tree_paths: list[str],
    ) -> tuple[float, bool]:
        score = 0.0

        # Framework presence
        verified_deps = [f for f in frameworks if f.verified_in_dependencies]
        if verified_deps:
            score += min(len(verified_deps) * 0.25, 0.50)
        elif frameworks:
            score += 0.20

        # ML code files
        if ml_code_files:
            score += min(len(ml_code_files) * 0.10, 0.30)

        # Notebooks
        has_notebooks = any(p.endswith(".ipynb") for p in tree_paths)
        if has_notebooks:
            score += 0.10

        # README ML keywords
        ml_keywords = [
            "model",
            "training",
            "dataset",
            "neural network",
            "machine learning",
            "deep learning",
            "inference",
        ]
        readme_kw_count = sum(1 for kw in ml_keywords if kw in readme_text.lower())
        score += min(readme_kw_count * 0.04, 0.20)

        confidence = min(max(score, 0.0), 1.0)
        is_ml = confidence >= 0.35
        return confidence, is_ml

    def _generate_summary_notes(
        self,
        repo: str,
        is_ml: bool,
        frameworks: list[FrameworkItem],
        problem: AnalysisField,
        architecture: AnalysisField,
        datasets: AnalysisField,
        pipeline: AnalysisField,
        eval_metrics: AnalysisField,
        deployment: AnalysisField,
    ) -> str:
        verified_fws = [f.name for f in frameworks if f.verified_in_dependencies]
        all_fws = [f.name for f in frameworks]

        lines = []
        if is_ml:
            lines.append(f"Repository '{repo}' is identified as a Machine Learning project.")
            if verified_fws:
                lines.append(f"- Verified ML stack: {', '.join(verified_fws)}.")
            elif all_fws:
                lines.append(f"- Mentioned ML stack: {', '.join(all_fws)}.")
        else:
            lines.append(f"Repository '{repo}' shows low confidence as a dedicated ML project.")

        lines.append(f"- Problem Statement: [{problem.status.upper()}] {problem.details}")
        lines.append(f"- Architecture: [{architecture.status.upper()}] {architecture.details}")
        lines.append(f"- Datasets: [{datasets.status.upper()}] {datasets.details}")
        lines.append(f"- Training Pipeline: [{pipeline.status.upper()}] {pipeline.details}")
        lines.append(f"- Evaluation: [{eval_metrics.status.upper()}] {eval_metrics.details}")
        lines.append(f"- Deployment: [{deployment.status.upper()}] {deployment.details}")

        # Gap analysis
        unverified = [
            name
            for name, field in [
                ("Problem Statement", problem),
                ("Model Architecture", architecture),
                ("Datasets", datasets),
                ("Training Pipeline", pipeline),
                ("Evaluation Metrics", eval_metrics),
                ("Deployment", deployment),
            ]
            if field.status == "unverified"
        ]
        if unverified:
            lines.append(
                f"- Portfolio Improvement Opportunity: Document or implement missing artifacts for: {', '.join(unverified)}."
            )

        return "\n".join(lines)
