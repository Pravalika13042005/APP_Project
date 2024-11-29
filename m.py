import threading
from tkinter import *
from tkinter import messagebox
import pandas as pd
from PIL import Image, ImageTk
import requests
from io import BytesIO

# Load the dataset
movies_df = pd.read_csv('topmovies.csv')

# Recommendation functions
def recommend_by_genre(genre, min_rating):
    filtered_df = movies_df[movies_df['Genre'].str.contains(genre, case=False, na=False)]
    if min_rating:
        filtered_df = filtered_df[filtered_df['IMDB_Rating'] >= min_rating]
    return filtered_df

def recommend_by_title(title, min_rating):
    filtered_df = movies_df[movies_df['Series_Title'].str.contains(title, case=False, na=False)]
    if min_rating:
        filtered_df = filtered_df[filtered_df['IMDB_Rating'] >= min_rating]
    return filtered_df

# Initialize an in-memory list to store favorite movies
favorite_movies_list = []

# Function to load the image in a separate thread
def load_image_async(movie_poster_url, callback, movie_frame):
    def load_image():
        try:
            response = requests.get(movie_poster_url)
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            img.thumbnail((100, 150))  # Resize
            poster_img = ImageTk.PhotoImage(img)
            callback(poster_img, movie_frame)  # Update the UI in the main thread
        except Exception as e:
            callback(None, movie_frame)  # Handle errors in case of bad image links
    threading.Thread(target=load_image).start()

# Update UI with image
def update_image(poster_img, movie_frame):
    if poster_img:
        poster_label = Label(movie_frame, image=poster_img, bg="#f9f9f9")
        poster_label.image = poster_img
        poster_label.grid(row=0, column=0, rowspan=2, padx=10)
    else:
        Label(movie_frame, text="No Image", bg="#f9f9f9").grid(row=0, column=0, rowspan=2, padx=10)

# Function to save the selected movie to favorites
def save_movie(movie_title, movie_details):
    if movie_title not in [movie['Title'] for movie in favorite_movies_list]:
        favorite_movies_list.append(movie_details)
        messagebox.showinfo("Saved", f"Movie '{movie_title}' saved to favorites.")
    else:
        messagebox.showinfo("Already Saved", f"Movie '{movie_title}' is already in your favorites.")

# Function to display favorite movies
def show_favorites():
    if not favorite_movies_list:
        messagebox.showinfo("Favorites", "You have no saved favorite movies.")
        return

    for widget in results_canvas_frame.winfo_children():
        widget.destroy()

    for movie in favorite_movies_list:
        movie_title = movie['Title']
        movie_year = movie['Year']
        movie_rating = movie['Rating']
        movie_poster_url = movie['Poster']

        movie_frame = Frame(results_canvas_frame, bg="#f9f9f9", padx=10, pady=10, relief=SOLID, bd=1)
        movie_frame.pack(fill=X, pady=5)

        details_text = f"Title: {movie_title}\nYear: {movie_year}\nRating: {movie_rating}"
        details_label = Label(movie_frame, text=details_text, bg="#f9f9f9", font=("Helvetica", 12), justify=LEFT, anchor="w")
        details_label.grid(row=0, column=1, sticky="w")

        load_image_async(movie_poster_url, update_image, movie_frame)

# Display recommendations
def display_recommendations(recommendations):
    if recommendations.empty:
        messagebox.showinfo("No Results", "No movies found. Please try different inputs.")
        return

    for widget in results_canvas_frame.winfo_children():
        widget.destroy()

    for index, movie in recommendations.iterrows():
        movie_title = movie['Series_Title']
        movie_year = movie['Released_Year']
        movie_rating = movie['IMDB_Rating']
        movie_poster_url = movie['Poster_Link']

        movie_details = {
            'Title': movie_title,
            'Year': movie_year,
            'Rating': movie_rating,
            'Poster': movie_poster_url
        }

        movie_frame = Frame(results_canvas_frame, bg="#f9f9f9", padx=10, pady=10, relief=SOLID, bd=1)
        movie_frame.pack(fill=X, pady=5)

        details_text = f"Title: {movie_title}\nYear: {movie_year}\nRating: {movie_rating}"
        details_label = Label(movie_frame, text=details_text, bg="#f9f9f9", font=("Helvetica", 12), justify=LEFT, anchor="w")
        details_label.grid(row=0, column=1, sticky="w")

        load_image_async(movie_poster_url, update_image, movie_frame)

        save_button = Button(movie_frame, text="Save", command=lambda title=movie_title, details=movie_details: save_movie(title, details), bg="#4b79a1", fg="white", font=("Helvetica", 12))
        save_button.grid(row=1, column=2, padx=10)

# Genre button callback with additional filter options
def display_recommendations_by_genre():
    genre = genre_entry.get()
    min_rating = float(min_rating_entry.get()) if min_rating_entry.get() else None

    if not genre:
        messagebox.showerror("Input Error", "Please enter a genre.")
        return

    recommendations = recommend_by_genre(genre, min_rating)
    display_recommendations(recommendations)

# Title button callback with additional filter options
# Title button callback with additional filter options
# Title button callback with additional filter options
def display_recommendations_by_title():
    title = title_entry.get()
    min_rating = float(min_rating_entry.get()) if min_rating_entry.get() else None

    if not title:
        messagebox.showerror("Input Error", "Please enter a movie name.")
        return

    # Step 1: Find the searched movie by title
    recommendations = recommend_by_title(title, min_rating)

    if recommendations.empty:
        messagebox.showinfo("No Results", "No movie found with that title.")
        return

    # Step 2: Get the genre of the first movie from the recommendations
    genre_of_searched_movie = recommendations.iloc[0]['Genre']

    # Print the genre of the searched movie (just for debugging)
    print(f"Genre of '{title}': {genre_of_searched_movie}")

    # Step 3: Get other movies from the same genre
    related_movies = recommend_by_genre(genre_of_searched_movie, min_rating)

    # Combine the searched movie with related movies
    combined_recommendations = pd.concat([recommendations, related_movies]).drop_duplicates()

    # Step 4: Clear previous results before displaying new ones
    for widget in results_canvas_frame.winfo_children():
        widget.destroy()

    # Display searched movie (with heading)
    display_recommendations_with_heading("Searched Movie", recommendations)

    # Display related movies (with heading)
    display_recommendations_with_heading(f"Related Movies of Genre: {genre_of_searched_movie}", related_movies)

# Function to display recommendations with a heading
def display_recommendations_with_heading(heading, recommendations):
    if recommendations.empty:
        return

    # Add heading label
    heading_label = Label(results_canvas_frame, text=heading, font=("Helvetica", 14, "bold"), bg="#f9f9f9", anchor="w")
    heading_label.pack(fill=X, pady=5)

    for index, movie in recommendations.iterrows():
        movie_title = movie['Series_Title']
        movie_year = movie['Released_Year']
        movie_rating = movie['IMDB_Rating']
        movie_poster_url = movie['Poster_Link']

        movie_details = {
            'Title': movie_title,
            'Year': movie_year,
            'Rating': movie_rating,
            'Poster': movie_poster_url
        }

        movie_frame = Frame(results_canvas_frame, bg="#f9f9f9", padx=10, pady=10, relief=SOLID, bd=1)
        movie_frame.pack(fill=X, pady=5)

        details_text = f"Title: {movie_title}\nYear: {movie_year}\nRating: {movie_rating}"
        details_label = Label(movie_frame, text=details_text, bg="#f9f9f9", font=("Helvetica", 12), justify=LEFT, anchor="w")
        details_label.grid(row=0, column=1, sticky="w")

        load_image_async(movie_poster_url, update_image, movie_frame)

        save_button = Button(movie_frame, text="Save", command=lambda title=movie_title, details=movie_details: save_movie(title, details), bg="#4b79a1", fg="white", font=("Helvetica", 12))
        save_button.grid(row=1, column=2, padx=10)

# Main application
root = Tk()
root.title("Movie Recommendation App")
root.geometry("800x600")
root.configure(bg="#f0f0f5")

# App title
title_frame = Frame(root, bg="#4b79a1", height=120)
title_frame.pack(fill=X)

app_title = Label(
    title_frame,
    text="Movie Recommendation App",
    font=("Helvetica", 24, "bold"),
    bg="#4b79a1",
    fg="white",
    pady=20
)
app_title.pack()

# Bottom Content
content_frame = Frame(root, bg="#f0f0f5")
content_frame.pack(fill=BOTH, expand=True)

# Left Panel
input_frame = Frame(content_frame, bg="#d1e8e2", width=320, padx=20, pady=20)
input_frame.pack(side=LEFT, fill=Y)

Label(input_frame, text="Enter Genre:", bg="#d1e8e2", font=("Helvetica", 14)).pack(anchor=W, pady=5)
genre_entry = Entry(input_frame, font=("Helvetica", 12), width=30)
genre_entry.pack(pady=5)

Label(input_frame, text="Minimum IMDB Rating:", bg="#d1e8e2", font=("Helvetica", 14)).pack(anchor=W, pady=5)
min_rating_entry = Entry(input_frame, font=("Helvetica", 12), width=30)
min_rating_entry.pack(pady=5)

genre_button = Button(input_frame, text="Search by Genre", command=display_recommendations_by_genre, bg="#4b79a1", fg="white", font=("Helvetica", 12), width=20)
genre_button.pack(pady=10)

Label(input_frame, text="Enter Movie Name:", bg="#d1e8e2", font=("Helvetica", 14)).pack(anchor=W, pady=5)
title_entry = Entry(input_frame, font=("Helvetica", 12), width=30)
title_entry.pack(pady=5)

title_button = Button(input_frame, text="Search by Title", command=display_recommendations_by_title, bg="#4b79a1", fg="white", font=("Helvetica", 12), width=20)
title_button.pack(pady=10)

favorite_button = Button(input_frame, text="Show Favorites", command=show_favorites, bg="#4b79a1", fg="white", font=("Helvetica", 12), width=20)
favorite_button.pack(pady=10)

# Right Panel for displaying results with scrollable canvas
right_panel_frame = Frame(content_frame, bg="#f9f9f9")
right_panel_frame.pack(side=RIGHT, fill=BOTH, expand=True)

# Create a canvas for scrollable content
canvas = Canvas(right_panel_frame)
canvas.pack(side=LEFT, fill=BOTH, expand=True)

# Add a scrollbar for the canvas
scrollbar = Scrollbar(right_panel_frame, orient=VERTICAL, command=canvas.yview)
scrollbar.pack(side=RIGHT, fill=Y)
canvas.config(yscrollcommand=scrollbar.set)

# Create a frame inside the canvas to hold the movie results
results_canvas_frame = Frame(canvas, bg="#f9f9f9")
canvas.create_window((0, 0), window=results_canvas_frame, anchor="nw")

# Update scroll region when new content is added
def on_frame_configure(event):
    canvas.config(scrollregion=canvas.bbox("all"))

results_canvas_frame.bind("<Configure>", on_frame_configure)

root.mainloop()