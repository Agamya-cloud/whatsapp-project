# @app.route("/chat/<int:receiver_id>")
# def chat_with_user(receiver_id):
#     """Chat with a specific user."""
#     if "user_id" not in session:
#         return redirect(url_for("phone_login"))

#     user = User.query.get(session["user_id"])

#     if not user:
#         flash("User not found! Please log in again.", "danger")
#         session.clear()
#         return redirect(url_for("phone_login"))

#     receiver = User.query.get(receiver_id)

#     if not receiver:
#         flash("Receiver not found!", "danger")
#         return render_template("no_chat_available.html")  # ✅ Proper handling

#     return render_template("chat.html", user=user, receiver=receiver)