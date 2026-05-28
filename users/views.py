from datetime import datetime
from pathlib import Path

import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from .forms import UserRegistrationForm
from .models import UserRegistrationModel


PREDICTION_LOG = Path(settings.MEDIA_ROOT) / "prediction_logs.txt"
PROFILE_PREDICTION_TABLE = Path(settings.MEDIA_ROOT) / "profile_predictions.txt"


def _ensure_media_root():
    Path(settings.MEDIA_ROOT).mkdir(parents=True, exist_ok=True)


def _read_lines(path):
    _ensure_media_root()
    if path.exists():
        return path.read_text(encoding="utf-8").splitlines()
    return []


def _append_text(path, text):
    _ensure_media_root()
    with path.open("a", encoding="utf-8") as file:
        file.write(text)


def _table_logs():
    lines = _read_lines(PROFILE_PREDICTION_TABLE)
    rows = []
    for line in lines:
        if not line.strip() or line.startswith("Timestamp") or line.startswith("-"):
            continue
        rows.append([value.strip() for value in line.split("|")])
    return rows


def UserRegisterActions(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "You have been successfully registered. Please wait for admin activation.")
            form = UserRegistrationForm()
        else:
            messages.error(request, "Please check the form. Login ID, mobile, or email may already exist.")
    else:
        form = UserRegistrationForm()
    return render(request, "UserRegistrations.html", {"form": form})


def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get("loginid", "").strip()
        pswd = request.POST.get("pswd", "")
        try:
            user = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            if user.status == "activated":
                request.session["id"] = user.id
                request.session["loggeduser"] = user.name
                request.session["loginid"] = loginid
                request.session["email"] = user.email
                return render(request, "users/UserHomePage.html", {})
            messages.warning(request, "Your account is not activated yet. Please contact the admin.")
        except UserRegistrationModel.DoesNotExist:
            messages.error(request, "Invalid login ID or password.")
    return render(request, "UserLogin.html", {})


def UserHome(request):
    return render(request, "users/UserHomePage.html", {})


def DatasetView(request):
    dataset_path = Path(settings.MEDIA_ROOT) / "train.csv"
    if not dataset_path.exists():
        return render(request, "users/viewdataset.html", {"data": "<p>Dataset file not found.</p>"})

    df = pd.read_csv(dataset_path, nrows=100)
    html_table = df.to_html(classes="table table-striped table-bordered", index=False)
    return render(request, "users/viewdataset.html", {"data": html_table})


def training(request):
    """Train the ANN only when TensorFlow is installed.

    The normal website and prediction page should run even on lightweight hosts
    where TensorFlow is not installed.
    """
    try:
        import numpy as np
        import tensorflow as tf
        from sklearn.metrics import classification_report, confusion_matrix
        from sklearn.preprocessing import StandardScaler
        from tensorflow.keras.layers import Dense, Dropout
        from tensorflow.keras.models import Sequential
    except Exception as exc:
        return render(
            request,
            "users/training.html",
            {
                "acc": "Training is unavailable because TensorFlow is not installed on this host.",
                "loss": str(exc),
            },
        )

    train_path = Path(settings.MEDIA_ROOT) / "train.csv"
    test_path = Path(settings.MEDIA_ROOT) / "test.csv"
    if not train_path.exists() or not test_path.exists():
        return render(request, "users/training.html", {"acc": "Dataset missing", "loss": "train.csv/test.csv not found"})

    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)

    X_train = train.drop(columns=["fake"])
    X_test = test.drop(columns=["fake"])
    y_train = train["fake"]
    y_test = test["fake"]

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    y_train_encoded = tf.keras.utils.to_categorical(y_train, num_classes=2)
    y_test_encoded = tf.keras.utils.to_categorical(y_test, num_classes=2)

    model = Sequential(
        [
            Dense(50, input_dim=X_train.shape[1], activation="relu"),
            Dense(150, activation="relu"),
            Dropout(0.3),
            Dense(25, activation="relu"),
            Dropout(0.3),
            Dense(2, activation="softmax"),
        ]
    )
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    history = model.fit(X_train, y_train_encoded, epochs=20, verbose=0, validation_split=0.1)
    model.save(settings.BASE_DIR / "model.h5")

    predicted = model.predict(X_test, verbose=0)
    predicted_value = [np.argmax(row) for row in predicted]
    actual_value = [np.argmax(row) for row in y_test_encoded]
    print(classification_report(actual_value, predicted_value))
    print(confusion_matrix(actual_value, predicted_value))

    acc = round(history.history["accuracy"][-1] * 100, 2)
    loss = round(history.history["loss"][-1], 4)
    return render(request, "users/training.html", {"acc": f"{acc}%", "loss": loss})


def predictTrustWorthy(request):
    if request.method == "POST":
        try:
            uploaded_file = request.FILES.get("profile_pic")
            fs = FileSystemStorage()
            file_url = None
            profile_pic = 0

            if uploaded_file:
                saved_name = fs.save(uploaded_file.name, uploaded_file)
                file_url = fs.url(saved_name)
                profile_pic = 1

            full_name = request.POST.get("full_name", "").strip()

            # Dataset uses ratio values for nums_length_username, normally 0.0 to 1.0
            raw_username_value = float(request.POST.get("nums_length_username", 0) or 0)
            nums_length_username = raw_username_value
            if nums_length_username > 1:
                nums_length_username = nums_length_username / 10
            nums_length_username = max(0, min(nums_length_username, 1))

            fullname_words = len(full_name.split()) if full_name else 0
            nums_length_fullname = sum(c.isdigit() for c in full_name)
            name_username = int(request.POST.get("name_username", 0) or 0)
            description_length = int(request.POST.get("description_length", 0) or 0)
            external_URL = int(request.POST.get("external_URL", 0) or 0)
            private = int(request.POST.get("private", 0) or 0)
            posts = int(request.POST.get("posts", 0) or 0)
            followers = int(request.POST.get("followers", 0) or 0)
            follows = int(request.POST.get("follows", 0) or 0)

            train_path = Path(settings.MEDIA_ROOT) / "train.csv"

            if not train_path.exists():
                return render(
                    request,
                    "users/predictForm.html",
                    {"msg": "Error: train.csv file not found in media folder."}
                )

            df = pd.read_csv(train_path)

            features = [
                "profile_pic",
                "nums_length_username",
                "fullname_words",
                "nums_length_fullname",
                "name_username",
                "description_length",
                "external_URL",
                "private",
                "posts",
                "followers",
                "follows",
            ]

            X_train = df[features]
            y_train = df["fake"]

            model = RandomForestClassifier(
                n_estimators=200,
                criterion="entropy",
                random_state=101,
                class_weight="balanced"
            )
            model.fit(X_train, y_train)

            test_df = pd.DataFrame(
                [{
                    "profile_pic": profile_pic,
                    "nums_length_username": nums_length_username,
                    "fullname_words": fullname_words,
                    "nums_length_fullname": nums_length_fullname,
                    "name_username": name_username,
                    "description_length": description_length,
                    "external_URL": external_URL,
                    "private": private,
                    "posts": posts,
                    "followers": followers,
                    "follows": follows,
                }]
            )

            y_pred = int(model.predict(test_df)[0])

            print("Prediction input:")
            print(test_df)
            print("Prediction result:", y_pred)

            if y_pred == 0:
                msg = "This is a genuine profile (fake profile = 0)"
            else:
                msg = "This is a fake profile (fake profile = 1)"

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            table_header = (
                "Timestamp | Full Name | Profile Pic | Nums in Username | "
                "Fullname Words | Nums in Fullname | Name in Username | "
                "Description Length | External URL | Private | Posts | Followers | Follows | Prediction\n"
            )

            table_line = (
                f"{timestamp} | {full_name} | {profile_pic} | {nums_length_username} | "
                f"{fullname_words} | {nums_length_fullname} | {name_username} | "
                f"{description_length} | {external_URL} | {private} | {posts} | "
                f"{followers} | {follows} | {y_pred}\n"
            )

            if not PROFILE_PREDICTION_TABLE.exists():
                _append_text(PROFILE_PREDICTION_TABLE, table_header + ("-" * 100) + "\n")

            _append_text(PROFILE_PREDICTION_TABLE, table_line)

            log_line = (
                f"[{timestamp}] Full Name: {full_name}, Profile Pic: {profile_pic}, "
                f"Followers: {followers}, Follows: {follows}, "
                f"Prediction (0 = real, 1 = fake): {y_pred}\n"
            )

            _append_text(PREDICTION_LOG, log_line)

            return render(
                request,
                "users/predictForm.html",
                {
                    "msg": msg,
                    "file_url": file_url,
                    "prediction_logs": _read_lines(PREDICTION_LOG),
                },
            )

        except Exception as exc:
            return render(
                request,
                "users/predictForm.html",
                {
                    "msg": f"Error: {exc}",
                    "prediction_logs": _read_lines(PREDICTION_LOG),
                },
            )

    return render(request, "users/predictForm.html")

def report_view(request):
    return render(request, "users/report.html", {"predictions": _table_logs()})


def report(request):
    rows = [[line] for line in _read_lines(PREDICTION_LOG) if line.strip()]
    return render(request, "users/result.html", {"predictions": rows})
