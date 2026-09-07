"""Seed the database with demo data for immediate demonstration."""

from sqlalchemy.orm import Session
from .database import SessionLocal
from .models.user import User
from .models.subject import Subject
from .models.topic import Topic
from .models.question import Question
from .auth import hash_password


def seed_demo_data():
    """Create demo student + ML subject with topics and questions if they don't exist."""
    db: Session = SessionLocal()
    try:
        # Skip if already seeded
        if db.query(Subject).filter(Subject.name == "Machine Learning").first():
            return

        # ── Demo User ──────────────────────────────────────────────
        demo_user = User(
            name="Demo Student",
            email="demo@adaptivelearn.com",
            password=hash_password("demo123"),
        )
        db.add(demo_user)
        db.flush()

        # ── Subjects ───────────────────────────────────────────────
        ml_subject = Subject(
            name="Machine Learning",
            department="Information Technology",
            education="B.Tech",
            year="2nd Year",
        )
        db.add(ml_subject)
        db.flush()

        # Additional subjects for variety
        for subj_data in [
            ("Python Programming", "Computer Science", "B.Tech", "1st Year"),
            ("Data Structures", "Computer Science", "B.Tech", "2nd Year"),
            ("Database Management Systems", "Information Technology", "B.Tech", "2nd Year"),
            ("Computer Networks", "Information Technology", "B.Tech", "3rd Year"),
            ("Operating Systems", "Computer Science", "B.Tech", "3rd Year"),
            ("Python Programming", "Computer Science", "BCA", "1st Year"),
            ("Data Structures", "Information Technology", "BCA", "2nd Year"),
            ("Machine Learning", "Computer Science", "MCA", "2nd Year"),
        ]:
            db.add(Subject(name=subj_data[0], department=subj_data[1], education=subj_data[2], year=subj_data[3]))

        # ── ML Topics ──────────────────────────────────────────────
        topics_data = [
            {
                "name": "Introduction to Machine Learning",
                "difficulty": "easy",
                "order_number": 1,
                "description": "Understand what Machine Learning is, its history, types, and applications.",
                "introduction": "Machine Learning is a subset of Artificial Intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing algorithms that can access data and use it to learn for themselves.",
                "explanation": "Machine Learning (ML) is the science of teaching computers to recognize patterns in data and make decisions with minimal human intervention. Instead of writing explicit rules, we provide examples (training data), and the algorithm figures out the rules on its own.\n\nThere are three main types:\n1. **Supervised Learning** — Learning from labeled examples (e.g., classifying emails as spam or not spam)\n2. **Unsupervised Learning** — Finding hidden patterns in unlabeled data (e.g., grouping customers by behavior)\n3. **Reinforcement Learning** — Learning through trial and error with rewards (e.g., a robot learning to walk)",
                "basic_example": "Imagine you want to teach a computer to distinguish between apples and oranges. Instead of writing rules about color, size, and shape, you show it hundreds of labeled images of apples and oranges. The computer learns the patterns itself — this is Machine Learning in its simplest form.",
                "advanced_example": "Netflix uses ML to recommend shows. It analyzes your viewing history, compares it with millions of other users, and predicts what you'd enjoy watching next. The algorithm continuously improves as more data becomes available, making recommendations more accurate over time.",
                "key_points": "• ML is a subset of AI focused on learning from data\n• Three main types: Supervised, Unsupervised, Reinforcement\n• Requires quality data for good performance\n• Used in recommendation systems, image recognition, NLP, and more\n• The model improves with more data and experience",
                "resources": "• Andrew Ng's Machine Learning Course (Coursera)\n• 'Hands-On Machine Learning' by Aurélien Géron\n• scikit-learn documentation\n• Google ML Crash Course",
                "study_time_minutes": 30,
            },
            {
                "name": "Supervised Learning",
                "difficulty": "easy",
                "order_number": 2,
                "description": "Learn about supervised learning: classification, regression, training, and evaluation.",
                "introduction": "Supervised Learning is the most common type of Machine Learning. In supervised learning, the algorithm learns from labeled training data — each example comes with the correct answer (label). The goal is to learn a mapping function from inputs to outputs.",
                "explanation": "In Supervised Learning, we train a model using input-output pairs. Think of it like a student learning with an answer key.\n\n**Two main categories:**\n1. **Classification** — Predicting a category (discrete output)\n   - Email spam detection (spam / not spam)\n   - Image classification (cat / dog / bird)\n   - Disease diagnosis (positive / negative)\n\n2. **Regression** — Predicting a number (continuous output)\n   - House price prediction\n   - Temperature forecasting\n   - Stock price estimation\n\n**Key concepts:**\n- **Training Set** — Data used to train the model\n- **Test Set** — Data used to evaluate performance\n- **Overfitting** — Model memorizes training data but fails on new data\n- **Underfitting** — Model is too simple to capture patterns",
                "basic_example": "A teacher shows a student 100 flashcards with animals and their names. After studying these labeled examples, the student can identify new animals they've never seen before. This is how supervised learning works — learning from labeled examples.",
                "advanced_example": "A bank wants to predict loan defaults. They use historical data (income, credit score, employment history → defaulted or not) to train a classifier. The model learns patterns: low credit score + high debt = likely default. When a new application comes in, the model predicts the probability of default.",
                "key_points": "• Uses labeled training data (input → output pairs)\n• Classification predicts categories, Regression predicts numbers\n• Requires splitting data into training and test sets\n• Watch out for overfitting and underfitting\n• Common algorithms: Linear Regression, Decision Trees, SVM, Neural Networks",
                "resources": "• StatQuest YouTube series on ML\n• 'Pattern Recognition and Machine Learning' by Bishop\n• Kaggle supervised learning tutorials\n• scikit-learn classification and regression guides",
                "study_time_minutes": 35,
            },
            {
                "name": "Regression",
                "difficulty": "medium",
                "order_number": 3,
                "description": "Understand regression techniques: linear regression, polynomial regression, and evaluation metrics.",
                "introduction": "Regression is a supervised learning technique used to predict continuous numerical values. The most common form is Linear Regression, which finds the best-fit line through the data points.",
                "explanation": "Regression helps us answer 'how much?' or 'how many?' questions.\n\n**Linear Regression:**\n- Finds the equation: y = mx + b (a straight line)\n- 'm' is the slope (how much y changes per unit of x)\n- 'b' is the intercept (value of y when x = 0)\n- Goal: minimize the error between predicted and actual values\n\n**Evaluation Metrics:**\n- **MSE** (Mean Squared Error) — Average of squared differences\n- **RMSE** (Root Mean Squared Error) — Square root of MSE\n- **R² Score** — How well the model fits (1.0 = perfect)\n\n**Polynomial Regression:**\n- When data isn't linear, we can fit a curve\n- Uses polynomial features (x², x³, etc.)\n- More flexible but risks overfitting",
                "basic_example": "Predicting house prices based on size. If you plot size (x-axis) vs price (y-axis), linear regression draws the best straight line through all the data points. A 1000 sq ft house might be predicted at $200,000, a 2000 sq ft at $400,000, etc.",
                "advanced_example": "A company predicts monthly revenue using multiple features: advertising spend, number of employees, and season. This is Multiple Linear Regression: Revenue = β₀ + β₁(ads) + β₂(employees) + β₃(season). Each coefficient tells how much that factor contributes to revenue.",
                "key_points": "• Predicts continuous numerical values\n• Linear Regression finds the best-fit line\n- Key metrics: MSE, RMSE, R² Score\n• Polynomial Regression handles non-linear data\n• Multiple Regression uses multiple input features",
                "resources": "• Khan Academy — Regression analysis\n• 'An Introduction to Statistical Learning' (Chapter 3)\n• StatQuest: Linear Regression playlist\n• scikit-learn Linear Regression tutorial",
                "study_time_minutes": 40,
            },
            {
                "name": "Classification",
                "difficulty": "medium",
                "order_number": 4,
                "description": "Learn classification algorithms: logistic regression, KNN, and evaluation metrics.",
                "introduction": "Classification is a supervised learning technique used to predict discrete categories or classes. It assigns data points to one of several predefined groups based on their features.",
                "explanation": "Classification answers 'which category?' questions.\n\n**Common Algorithms:**\n1. **Logistic Regression** — Despite the name, it's for classification. Uses sigmoid function to output probabilities between 0 and 1.\n2. **K-Nearest Neighbors (KNN)** — Classifies based on the majority class of K nearest data points.\n3. **Support Vector Machine (SVM)** — Finds the best boundary (hyperplane) between classes.\n\n**Evaluation Metrics:**\n- **Accuracy** — % of correct predictions\n- **Precision** — Of all positive predictions, how many were correct?\n- **Recall** — Of all actual positives, how many did we catch?\n- **F1 Score** — Harmonic mean of Precision and Recall\n- **Confusion Matrix** — Table showing true/false positives and negatives",
                "basic_example": "Email spam detection: The algorithm looks at features like sender address, subject line keywords, and attachments. Based on patterns from thousands of labeled emails, it classifies new emails as 'spam' or 'not spam'.",
                "advanced_example": "A hospital uses classification to predict whether a tumor is benign or malignant. Features include size, shape, texture, and growth rate. The model (e.g., SVM) learns from thousands of past cases. High recall is critical here — missing a malignant tumor (false negative) is far worse than a false alarm.",
                "key_points": "• Predicts discrete categories/classes\n• Logistic Regression uses sigmoid for probability output\n• KNN classifies by majority vote of nearest neighbors\n• Key metrics: Accuracy, Precision, Recall, F1 Score\n• Confusion Matrix provides detailed error analysis",
                "resources": "• 'StatQuest: Classification' YouTube series\n• scikit-learn classification guide\n• Kaggle Titanic classification challenge\n• Andrew Ng's classification lecture notes",
                "study_time_minutes": 40,
            },
            {
                "name": "Decision Trees",
                "difficulty": "medium",
                "order_number": 5,
                "description": "Understand decision trees, splitting criteria, pruning, and ensemble methods.",
                "introduction": "Decision Trees are versatile ML algorithms that can be used for both classification and regression. They work by recursively splitting the data based on feature values, creating a tree-like structure of decisions.",
                "explanation": "A Decision Tree is like a flowchart of questions that lead to a decision.\n\n**How it works:**\n1. Start at the root node (all data)\n2. Find the best feature to split on (maximizes information gain)\n3. Split the data into subsets\n4. Repeat for each subset (recursive splitting)\n5. Stop when a condition is met (max depth, min samples)\n\n**Splitting Criteria:**\n- **Gini Impurity** — Measures how often a random element would be misclassified\n- **Information Gain (Entropy)** — Measures reduction in uncertainty\n- **Variance Reduction** — For regression trees\n\n**Problems & Solutions:**\n- **Overfitting** → Pruning, max depth limit\n- **Instability** → Random Forests (ensemble of trees)",
                "basic_example": "Deciding whether to play tennis based on weather:\n- Is it raining? → Yes → Is it windy? → Yes → Don't play / No → Play\n- Is it raining? → No → Is it sunny? → Yes → Don't play / No → Play\nEach question is a node, and the final decision is a leaf.",
                "advanced_example": "A telecom company uses a decision tree to predict customer churn. The tree learns: If contract_type = month-to-month AND monthly_charges > $70 AND tenure < 12 months → High churn risk. This gives actionable rules the business can use to retain customers.",
                "key_points": "• Works for both classification and regression\n• Easy to interpret and visualize\n• Uses Gini Impurity or Entropy for splitting\n• Prone to overfitting → use pruning\n• Ensemble methods (Random Forest, Gradient Boosting) improve performance",
                "resources": "• StatQuest: Decision Trees playlist\n• 'Hands-On ML' Chapter on Decision Trees\n• scikit-learn Decision Tree guide\n• Visualizing Decision Trees tutorial",
                "study_time_minutes": 35,
            },
            {
                "name": "Clustering",
                "difficulty": "medium",
                "order_number": 6,
                "description": "Learn unsupervised clustering: K-Means, hierarchical clustering, and applications.",
                "introduction": "Clustering is an unsupervised learning technique that groups similar data points together. Unlike classification, there are no predefined labels — the algorithm discovers the groups on its own.",
                "explanation": "Clustering finds hidden structure in unlabeled data.\n\n**K-Means Clustering:**\n1. Choose K (number of clusters)\n2. Randomly place K centroids\n3. Assign each point to the nearest centroid\n4. Move centroids to the center of their clusters\n5. Repeat steps 3-4 until convergence\n\n**Other Methods:**\n- **Hierarchical Clustering** — Builds a tree of clusters (dendrogram)\n- **DBSCAN** — Density-based, finds arbitrarily shaped clusters\n- **Gaussian Mixture Models** — Probabilistic approach\n\n**Choosing K:**\n- **Elbow Method** — Plot inertia vs K, look for the 'elbow'\n- **Silhouette Score** — Measures how similar points are to their own cluster vs other clusters",
                "basic_example": "Imagine a bag of mixed candies. Without knowing the types, you group them by color — all reds together, all greens together. That's clustering: grouping similar items without knowing the categories in advance.",
                "advanced_example": "An e-commerce platform uses K-Means to segment customers. Features: spending score, annual income, and purchase frequency. The algorithm reveals 5 customer segments: 'Budget Shoppers', 'Premium Buyers', 'Seasonal Shoppers', etc. Marketing then tailors campaigns to each segment.",
                "key_points": "• Unsupervised learning — no labels needed\n• K-Means is the most popular clustering algorithm\n• Choose K using Elbow Method or Silhouette Score\n• Hierarchical clustering creates a tree of clusters\n• Applications: customer segmentation, anomaly detection, image compression",
                "resources": "• StatQuest: K-Means Clustering\n• 'Hands-On ML' chapter on Clustering\n• scikit-learn Clustering guide\n• Visualizing clusters with PCA tutorial",
                "study_time_minutes": 35,
            },
            {
                "name": "Neural Networks",
                "difficulty": "hard",
                "order_number": 7,
                "description": "Introduction to neural networks: perceptrons, activation functions, backpropagation, and deep learning.",
                "introduction": "Neural Networks are computing systems inspired by the biological neural networks in the brain. They consist of interconnected nodes (neurons) organized in layers that process information and learn patterns from data.",
                "explanation": "Neural networks are the foundation of deep learning.\n\n**Structure:**\n- **Input Layer** — Receives the raw data\n- **Hidden Layers** — Process the data through weighted connections\n- **Output Layer** — Produces the final prediction\n\n**Key Concepts:**\n- **Neuron** — Takes inputs, applies weights, adds bias, passes through activation function\n- **Activation Functions:**\n  - ReLU: f(x) = max(0, x) — most common\n  - Sigmoid: f(x) = 1/(1+e^(-x)) — outputs 0 to 1\n  - Softmax: Converts outputs to probabilities\n- **Backpropagation** — Algorithm for updating weights based on error\n- **Learning Rate** — How much weights change per update\n\n**Deep Learning:**\n- Neural networks with many hidden layers\n- Can learn very complex patterns\n- Requires large data and computational power",
                "basic_example": "Teaching a neural network to recognize handwritten digits (0-9):\n- Input: 28x28 pixel image (784 input neurons)\n- Hidden layers: Learn to detect edges, curves, patterns\n- Output: 10 neurons (one per digit), highest value = prediction\n- After training on thousands of examples, it achieves >97% accuracy",
                "advanced_example": "A medical imaging system uses a Convolutional Neural Network (CNN) — a specialized neural network — to detect tumors in X-ray images. The network has millions of parameters organized in convolutional layers that detect edges, textures, and shapes hierarchically. It outperforms radiologists in some specific detection tasks.",
                "key_points": "• Inspired by biological neural networks\n• Consists of input, hidden, and output layers\n• Activation functions add non-linearity (ReLU, Sigmoid)\n• Backpropagation updates weights to minimize error\n• Deep Learning = neural networks with many layers\n• Powers modern AI: image recognition, NLP, game playing",
                "resources": "• 3Blue1Brown: Neural Networks series (YouTube)\n• 'Deep Learning' by Goodfellow, Bengio, Courville\n• TensorFlow/Keras beginner tutorial\n• Andrej Karpathy's 'Neural Networks: Zero to Hero'",
                "study_time_minutes": 45,
            },
        ]

        for td in topics_data:
            topic = Topic(subject_id=ml_subject.id, **td)
            db.add(topic)
        db.flush()

        # ── Seed hardcoded ML questions for each topic ─────────────
        ml_questions = _get_ml_questions(ml_subject.id, db)
        for topic_name, questions in ml_questions.items():
            topic = db.query(Topic).filter(
                Topic.subject_id == ml_subject.id, Topic.name == topic_name
            ).first()
            if topic:
                for q in questions:
                    db.add(Question(topic_id=topic.id, **q))

        db.commit()

    finally:
        db.close()


def _get_ml_questions(subject_id, db):
    """Return hardcoded quiz questions for each ML topic."""
    return {
        "Introduction to Machine Learning": [
            {"question": "What is Machine Learning?", "option_a": "A subset of AI that enables systems to learn from data", "option_b": "A programming language", "option_c": "A type of computer hardware", "option_d": "A database management technique", "correct_answer": "A", "explanation": "ML is a subset of AI focused on algorithms that learn from and make predictions on data."},
            {"question": "Which type of ML uses labeled data?", "option_a": "Unsupervised Learning", "option_b": "Reinforcement Learning", "option_c": "Supervised Learning", "option_d": "Clustering", "correct_answer": "C", "explanation": "Supervised learning uses labeled training data to learn the mapping from inputs to outputs."},
            {"question": "What is overfitting?", "option_a": "Model performs well on all data", "option_b": "Model memorizes training data but fails on new data", "option_c": "Model is too simple", "option_d": "Model uses too little data", "correct_answer": "B", "explanation": "Overfitting occurs when a model learns noise in the training data and cannot generalize."},
            {"question": "Netflix recommendations are an example of:", "option_a": "Robotics", "option_b": "Machine Learning application", "option_c": "Database management", "option_d": "Network security", "correct_answer": "B", "explanation": "Recommendation systems are a major application of ML, using patterns in user data."},
            {"question": "What are the three main types of Machine Learning?", "option_a": "Supervised, Unsupervised, Reinforcement", "option_b": "Linear, Non-linear, Polynomial", "option_c": "Simple, Complex, Hybrid", "option_d": "Static, Dynamic, Adaptive", "correct_answer": "A", "explanation": "The three main types are Supervised, Unsupervised, and Reinforcement Learning."},
            {"question": "In unsupervised learning, the data is:", "option_a": "Labeled", "option_b": "Unlabeled", "option_c": "Partially labeled", "option_d": "Pre-classified", "correct_answer": "B", "explanation": "Unsupervised learning works with unlabeled data, finding hidden patterns on its own."},
            {"question": "Reinforcement Learning learns through:", "option_a": "Labeled examples only", "option_b": "Trial and error with rewards", "option_c": "Clustering similar data", "option_d": "Manual programming", "correct_answer": "B", "explanation": "RL agents learn by taking actions and receiving rewards or penalties."},
            {"question": "Which is NOT a typical ML application?", "option_a": "Image recognition", "option_b": "Spam detection", "option_c": "Compiling source code", "option_d": "Recommendation systems", "correct_answer": "C", "explanation": "Compiling source code is a deterministic process, not a ML task."},
            {"question": "What does a training set provide?", "option_a": "Final answers for deployment", "option_b": "Examples for the model to learn patterns from", "option_c": "Hardware specifications", "option_d": "User interface designs", "correct_answer": "B", "explanation": "The training set provides labeled examples that the algorithm uses to learn."},
            {"question": "Why is data quality important in ML?", "option_a": "It makes the code run faster", "option_b": "Poor data leads to poor model performance", "option_c": "It reduces the need for algorithms", "option_d": "It eliminates the need for testing", "correct_answer": "B", "explanation": "The quality of data directly determines how well the model can learn and generalize."},
        ],
        "Supervised Learning": [
            {"question": "Supervised learning requires:", "option_a": "Unlabeled data", "option_b": "Labeled training data", "option_c": "No data at all", "option_d": "Only test data", "correct_answer": "B", "explanation": "Supervised learning needs labeled data where each example has the correct answer."},
            {"question": "Which is a classification problem?", "option_a": "Predicting house prices", "option_b": "Predicting temperature", "option_c": "Detecting spam emails", "option_d": "Estimating stock prices", "correct_answer": "C", "explanation": "Classification predicts categories (spam/not spam), while regression predicts numbers."},
            {"question": "Which is a regression problem?", "option_a": "Image classification", "option_b": "Predicting house prices", "option_c": "Spam detection", "option_d": "Disease diagnosis", "correct_answer": "B", "explanation": "Regression predicts continuous numerical values like prices."},
            {"question": "What is the purpose of a test set?", "option_a": "To train the model", "option_b": "To evaluate model performance on unseen data", "option_c": "To store data", "option_d": "To label data", "correct_answer": "B", "explanation": "The test set evaluates how well the model generalizes to new, unseen data."},
            {"question": "Underfitting occurs when:", "option_a": "Model is too complex", "option_b": "Model is too simple to capture patterns", "option_c": "Model memorizes training data", "option_d": "Model has too many features", "correct_answer": "B", "explanation": "Underfitting happens when the model is too simple and cannot learn the underlying patterns."},
            {"question": "Logistic Regression is used for:", "option_a": "Regression only", "option_b": "Classification", "option_c": "Clustering", "option_d": "Dimensionality reduction", "correct_answer": "B", "explanation": "Despite its name, Logistic Regression is primarily used for classification tasks."},
            {"question": "What does overfitting mean?", "option_a": "Model is too simple", "option_b": "Model performs equally on all data", "option_c": "Model memorizes training data but fails on new data", "option_d": "Model uses too few features", "correct_answer": "C", "explanation": "Overfitting means the model has learned the training data too well, including noise."},
            {"question": "Which algorithm is NOT supervised learning?", "option_a": "Linear Regression", "option_b": "Decision Tree", "option_c": "K-Means", "option_d": "SVM", "correct_answer": "C", "explanation": "K-Means is an unsupervised clustering algorithm."},
            {"question": "A confusion matrix is used for:", "option_a": "Regression evaluation", "option_b": "Classification evaluation", "option_c": "Data preprocessing", "option_d": "Feature selection", "correct_answer": "B", "explanation": "A confusion matrix shows the performance of a classification model."},
            {"question": "What is the mapping function in supervised learning?", "option_a": "A function that deletes data", "option_b": "A function that maps inputs to outputs", "option_c": "A function that creates labels", "option_d": "A function that splits data", "correct_answer": "B", "explanation": "The goal is to learn a function f: X → Y that maps inputs to outputs."},
        ],
        "Regression": [
            {"question": "Linear Regression predicts:", "option_a": "Categories", "option_b": "Continuous numerical values", "option_c": "Clusters", "option_d": "Binary labels", "correct_answer": "B", "explanation": "Regression predicts continuous values like prices, temperatures, or scores."},
            {"question": "In y = mx + b, what does 'm' represent?", "option_a": "The intercept", "option_b": "The slope", "option_c": "The error", "option_d": "The input", "correct_answer": "B", "explanation": "'m' is the slope — how much y changes for each unit change in x."},
            {"question": "What does R² score measure?", "option_a": "Model speed", "option_b": "How well the model fits the data", "option_c": "Number of features", "option_d": "Training time", "correct_answer": "B", "explanation": "R² measures the proportion of variance in the dependent variable explained by the model."},
            {"question": "MSE stands for:", "option_a": "Mean Simple Error", "option_b": "Mean Squared Error", "option_c": "Maximum Standard Error", "option_d": "Minimum Squared Error", "correct_answer": "B", "explanation": "MSE = Mean Squared Error — average of squared differences between predicted and actual values."},
            {"question": "Polynomial Regression is used when:", "option_a": "Data is linear", "option_b": "Data has a non-linear relationship", "option_c": "There is no data", "option_d": "Data is categorical", "correct_answer": "B", "explanation": "Polynomial regression fits curves to data that doesn't follow a straight line."},
            {"question": "Multiple Regression uses:", "option_a": "One input feature", "option_b": "Multiple input features", "option_c": "No features", "option_d": "Only output values", "correct_answer": "B", "explanation": "Multiple regression uses two or more independent variables to predict the output."},
            {"question": "RMSE is:", "option_a": "Square of MSE", "option_b": "Square root of MSE", "option_c": "Same as MSE", "option_d": "Double of MSE", "correct_answer": "B", "explanation": "RMSE = √MSE. It brings the error back to the original units."},
            {"question": "What does the intercept (b) represent?", "option_a": "The slope of the line", "option_b": "Value of y when x = 0", "option_c": "The error term", "option_d": "The number of data points", "correct_answer": "B", "explanation": "The intercept is where the regression line crosses the y-axis (x = 0)."},
            {"question": "Which metric is in the same units as the target variable?", "option_a": "MSE", "option_b": "RMSE", "option_c": "R²", "option_d": "Log Loss", "correct_answer": "B", "explanation": "RMSE is in the same units as the target because we take the square root of squared errors."},
            {"question": "A good R² score is close to:", "option_a": "0", "option_b": "-1", "option_c": "1", "option_d": "100", "correct_answer": "C", "explanation": "R² ranges from 0 to 1, where 1 means perfect fit."},
        ],
        "Classification": [
            {"question": "Classification predicts:", "option_a": "Continuous values", "option_b": "Discrete categories", "option_c": "Numbers only", "option_d": "Time series", "correct_answer": "B", "explanation": "Classification assigns data points to discrete categories or classes."},
            {"question": "The sigmoid function outputs values between:", "option_a": "-1 and 1", "option_b": "0 and 1", "option_c": "0 and 100", "option_d": "Any real number", "correct_answer": "B", "explanation": "The sigmoid function maps any input to a value between 0 and 1."},
            {"question": "KNN classifies based on:", "option_a": "Decision boundaries", "option_b": "Majority vote of K nearest neighbors", "option_c": "Probability distributions", "option_d": "Linear equations", "correct_answer": "B", "explanation": "KNN looks at the K closest data points and assigns the most common class."},
            {"question": "Precision measures:", "option_a": "All actual positives found", "option_b": "Of all positive predictions, how many were correct", "option_c": "Overall accuracy", "option_d": "Error rate", "correct_answer": "B", "explanation": "Precision = TP / (TP + FP). It measures the accuracy of positive predictions."},
            {"question": "Recall measures:", "option_a": "Of all actual positives, how many were correctly identified", "option_b": "False positive rate", "option_c": "Model speed", "option_d": "Number of features", "correct_answer": "A", "explanation": "Recall = TP / (TP + FN). It measures how many actual positives we caught."},
            {"question": "A confusion matrix shows:", "option_a": "Training time", "option_b": "True positives, false positives, true negatives, false negatives", "option_c": "Feature importance", "option_d": "Data distribution", "correct_answer": "B", "explanation": "The confusion matrix tabulates all four types of classification outcomes."},
            {"question": "SVM finds:", "option_a": "The mean of data", "option_b": "The best hyperplane to separate classes", "option_c": "Clusters in data", "option_d": "Regression line", "correct_answer": "B", "explanation": "SVM finds the optimal hyperplane that maximizes the margin between classes."},
            {"question": "F1 Score is the:", "option_a": "Average of precision and recall", "option_b": "Harmonic mean of precision and recall", "option_c": "Sum of precision and recall", "option_d": "Product of precision and recall", "correct_answer": "B", "explanation": "F1 = 2 × (Precision × Recall) / (Precision + Recall). It balances both metrics."},
            {"question": "When is high recall most important?", "option_a": "Spam detection", "option_b": "Cancer detection", "option_c": "Movie recommendations", "option_d": "Weather prediction", "correct_answer": "B", "explanation": "Missing a cancer case (false negative) is critical, so high recall is essential."},
            {"question": "Logistic Regression outputs:", "option_a": "Continuous values", "option_b": "Probabilities between 0 and 1", "option_c": "Clusters", "option_d": "Decision trees", "correct_answer": "B", "explanation": "Logistic regression uses sigmoid to output probabilities for classification."},
        ],
        "Decision Trees": [
            {"question": "A Decision Tree can be used for:", "option_a": "Only classification", "option_b": "Only regression", "option_c": "Both classification and regression", "option_d": "Neither", "correct_answer": "C", "explanation": "Decision Trees are versatile and work for both classification (CART) and regression."},
            {"question": "Gini Impurity measures:", "option_a": "Data size", "option_b": "How often a random element would be misclassified", "option_c": "Tree depth", "option_d": "Number of leaves", "correct_answer": "B", "explanation": "Gini Impurity quantifies the likelihood of incorrect classification of a random element."},
            {"question": "Pruning is used to:", "option_a": "Grow the tree deeper", "option_b": "Reduce overfitting by removing unnecessary branches", "option_c": "Add more features", "option_d": "Increase training time", "correct_answer": "B", "explanation": "Pruning removes branches that capture noise, reducing overfitting."},
            {"question": "The topmost node in a decision tree is called:", "option_a": "Leaf node", "option_b": "Root node", "option_c": "Branch node", "option_d": "Split node", "correct_answer": "B", "explanation": "The root node is the starting point that considers all the data."},
            {"question": "Information Gain uses which concept?", "option_a": "Variance", "option_b": "Entropy", "option_c": "Correlation", "option_d": "Standard deviation", "correct_answer": "B", "explanation": "Information Gain is based on Entropy — the reduction in uncertainty after a split."},
            {"question": "Leaf nodes represent:", "option_a": "Decisions to split", "option_b": "Final outcomes/predictions", "option_c": "Features", "option_d": "Training examples", "correct_answer": "B", "explanation": "Leaf nodes contain the final class label or predicted value."},
            {"question": "Random Forest is:", "option_a": "A single large decision tree", "option_b": "An ensemble of many decision trees", "option_c": "A type of neural network", "option_d": "A clustering algorithm", "correct_answer": "B", "explanation": "Random Forest combines multiple decision trees to improve accuracy and reduce overfitting."},
            {"question": "What happens if max_depth is not set?", "option_a": "Tree is very small", "option_b": "Tree may grow very deep and overfit", "option_c": "Tree won't grow", "option_d": "Tree runs faster", "correct_answer": "B", "explanation": "Without depth limit, the tree can grow until it perfectly memorizes training data."},
            {"question": "Decision Trees are easy to:", "option_a": "Overfit", "option_b": "Normalize", "option_c": "Parallelize", "option_d": "Regularize", "correct_answer": "A", "explanation": "Decision Trees are prone to overfitting, especially with deep trees."},
            {"question": "Which splitting criterion is used for regression trees?", "option_a": "Gini Impurity", "option_b": "Entropy", "option_c": "Variance Reduction (MSE)", "option_d": "Accuracy", "correct_answer": "C", "explanation": "Regression trees use variance reduction (minimizing MSE) to choose splits."},
        ],
        "Clustering": [
            {"question": "Clustering is a type of:", "option_a": "Supervised learning", "option_b": "Unsupervised learning", "option_c": "Reinforcement learning", "option_d": "Semi-supervised learning", "correct_answer": "B", "explanation": "Clustering is unsupervised — it finds hidden groups in unlabeled data."},
            {"question": "K-Means requires you to specify:", "option_a": "Labels", "option_b": "Number of clusters (K)", "option_c": "Features to ignore", "option_d": "Distance threshold", "correct_answer": "B", "explanation": "You must choose K, the number of clusters, before running K-Means."},
            {"question": "The Elbow Method helps to:", "option_a": "Train faster", "option_b": "Choose the optimal number of clusters", "option_c": "Label data", "option_d": "Reduce features", "correct_answer": "B", "explanation": "The Elbow Method plots inertia vs K and looks for the 'elbow' point."},
            {"question": "In K-Means, centroids are:", "option_a": "The outermost points", "option_b": "The center of each cluster", "option_c": "Random data points", "option_d": "The largest data points", "correct_answer": "B", "explanation": "Centroids are the mean position of all points in a cluster."},
            {"question": "DBSCAN is good at finding:", "option_a": "Only spherical clusters", "option_b": "Arbitrarily shaped clusters", "option_c": "Exactly K clusters", "option_d": "Labeled clusters", "correct_answer": "B", "explanation": "DBSCAN is density-based and can find clusters of any shape."},
            {"question": "Silhouette Score measures:", "option_a": "Training speed", "option_b": "How similar points are to their own cluster vs others", "option_c": "Number of iterations", "option_d": "Data size", "correct_answer": "B", "explanation": "Silhouette Score ranges from -1 to 1, measuring cluster quality."},
            {"question": "Customer segmentation is an application of:", "option_a": "Regression", "option_b": "Classification", "option_c": "Clustering", "option_d": "Reinforcement Learning", "correct_answer": "C", "explanation": "Segmentation groups customers by behavior — a classic clustering task."},
            {"question": "K-Means algorithm repeats until:", "option_a": "K changes", "option_b": "Centroids no longer change significantly", "option_c": "All points are removed", "option_d": "Data is deleted", "correct_answer": "B", "explanation": "K-Means converges when cluster assignments stop changing."},
            {"question": "Hierarchical clustering creates:", "option_a": "A flat list of clusters", "option_b": "A tree-like structure (dendrogram)", "option_c": "A single cluster", "option_d": "Random groups", "correct_answer": "B", "explanation": "Hierarchical clustering builds a dendrogram showing nested cluster relationships."},
            {"question": "A major limitation of K-Means is:", "option_a": "It's too slow for small data", "option_b": "You must specify K and it assumes spherical clusters", "option_c": "It can't handle numbers", "option_d": "It requires labeled data", "correct_answer": "B", "explanation": "K-Means needs K specified upfront and works best with spherical, equally-sized clusters."},
        ],
        "Neural Networks": [
            {"question": "A neural network is inspired by:", "option_a": "Computer circuits", "option_b": "Biological neural networks in the brain", "option_c": "Database structures", "option_d": "Sorting algorithms", "correct_answer": "B", "explanation": "Neural networks are inspired by the structure and function of biological brains."},
            {"question": "The ReLU activation function is:", "option_a": "f(x) = x²", "option_b": "f(x) = max(0, x)", "option_c": "f(x) = 1/x", "option_d": "f(x) = log(x)", "correct_answer": "B", "explanation": "ReLU outputs the input if positive, otherwise zero. It's the most common activation function."},
            {"question": "Backpropagation is used to:", "option_a": "Add more layers", "option_b": "Update weights by computing gradients of the loss", "option_c": "Preprocess data", "option_d": "Choose activation functions", "correct_answer": "B", "explanation": "Backpropagation computes gradients to update weights and reduce prediction error."},
            {"question": "The output layer of a classification network with 10 classes has:", "option_a": "1 neuron", "option_b": "5 neurons", "option_c": "10 neurons", "option_d": "100 neurons", "correct_answer": "C", "explanation": "Each output neuron represents the score for one class."},
            {"question": "Deep Learning refers to:", "option_a": "Shallow models", "option_b": "Neural networks with many hidden layers", "option_c": "Decision trees", "option_d": "Linear regression", "correct_answer": "B", "explanation": "Deep Learning = neural networks with multiple hidden layers."},
            {"question": "The softmax function converts outputs to:", "option_a": "Binary values", "option_b": "Probabilities that sum to 1", "option_c": "Negative numbers", "option_d": "Random values", "correct_answer": "B", "explanation": "Softmax converts raw scores into a probability distribution."},
            {"question": "Learning rate controls:", "option_a": "The number of layers", "option_b": "How much weights change during training", "option_c": "The size of input data", "option_d": "The number of epochs", "correct_answer": "B", "explanation": "Learning rate determines the step size for weight updates."},
            {"question": "CNNs are especially good at:", "option_a": "Text generation", "option_b": "Image recognition", "option_c": "Time series", "option_d": "Database queries", "correct_answer": "B", "explanation": "Convolutional Neural Networks excel at processing grid-like data such as images."},
            {"question": "A neuron in a neural network takes inputs, applies weights, and:", "option_a": "Stores them", "option_b": "Passes the result through an activation function", "option_c": "Deletes unnecessary ones", "option_d": "Returns them unchanged", "correct_answer": "B", "explanation": "Each neuron computes a weighted sum, adds bias, and applies an activation function."},
            {"question": "Which is NOT a common activation function?", "option_a": "ReLU", "option_b": "Sigmoid", "option_c": "Mean Squared Error", "option_d": "Tanh", "correct_answer": "C", "explanation": "MSE is a loss function, not an activation function."},
        ],
    }
