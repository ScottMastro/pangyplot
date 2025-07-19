import matplotlib.pyplot as plt 

def plot_bubbles(bubbles, output_path, min_height=None):
    bubble_dict = {bubble.id: bubble for bubble in bubbles}

    plt.figure(figsize=(12, 6))

    for bid, bubble in bubble_dict.items():
        if len(bubble["range"]) < 2: 
            continue
        if min_height is not None and bubble["height"] < min_height:
            continue
        
        x = bubble["range"]
        if len(x) == 1: x = [x] * 2

        y = [bubble["height"]] * 2
        plt.plot(x, y, color="blue", lw=2)

        #midpoint = sum(x) / 2
        #plt.text(midpoint, y_val + 0.05, f"{bid}", color="black", fontsize=6, ha="center")

    plt.xlabel("Reference Node ID")
    plt.ylabel("Height")
    plt.title("Bubbles over Reference Path")
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"[INFO] Plot saved to {output_path}")
