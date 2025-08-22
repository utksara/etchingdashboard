import vtk
import fft_reconstruct
import numpy as np


def get_dimensions(poly_data: vtk.vtkPolyData) -> tuple[float, float]:
    """
    Calculates the vertical distance between the min and max y-coordinates of all points.

    Args:
        poly_data (vtk.vtkPolyData): The VTK polydata object containing the points.

    Returns:
        float: The distance between the minimum and maximum y-coordinates.
    """
    points = poly_data.GetPoints()
    num_points = points.GetNumberOfPoints()

    if num_points == 0:
        return 0.0

    # Get the bounding box to quickly find min and max y
    bounds = poly_data.GetBounds()
    min_y = bounds[2]
    max_y = bounds[3]
    max_x = bounds[1]
    min_x = bounds[0]

    return max_x - min_x, max_y - min_y


def get_vtp_points(vtp_file_path: str) -> list[tuple[float, float]]:
    print(f"Reading VTP file from: {vtp_file_path}")

    # Create a VTK XML PolyData reader
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(vtp_file_path)
    reader.Update()

    # Get the polygonal data from the reader
    poly_data = reader.GetOutput()
    points = poly_data.GetPoints()

    num_points = points.GetNumberOfPoints()

    if num_points == 0:
        print("VTP file contains no points. No SVG will be generated.")
        return

    print(f"Found {num_points} points.")

    svg_points = []

    # Iterate through the points and add a circle element for each
    for i in range(num_points):
        point = points.GetPoint(i)
        svg_points.append(point)

    return svg_points


def points_to_svg(points: list[tuple[float, float]], svg_file_path: str) -> None:
    """
    Converts a list of points to an SVG file, plotting only the points as circles.

    Args:
        points (list): A list of tuples or lists representing the points (x, y).
        svg_file_path (str): The path for the output .svg file.
    """
    if not points:
        print("No points provided. No SVG will be generated.")
        return

    # Determine the bounding box to set the SVG viewBox
    x_coords, y_coords = zip(*points)
    x_min, x_max = np.min(x_coords), np.max(x_coords)
    y_min, y_max = np.min(y_coords), np.max(y_coords)
    width = x_max - x_min
    height = y_max - y_min

    # Use padding to ensure points on the edge are visible
    padding = max(width, height) * 0.05
    viewBox_x = x_min - padding
    viewBox_y = y_min - padding
    viewBox_width = width + 2 * padding
    viewBox_height = height + 2 * padding

    # A small fixed radius for the points
    point_radius = max(width, height) * 0.005
    if point_radius == 0:
        point_radius = 1  # Fallback for single-point or zero-bound data

    print(f"Found {len(points)} points.")

    # Start building the SVG content string
    svg_content = f"""
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="{viewBox_x} {viewBox_y} {viewBox_width} {viewBox_height}"
     width="800" height="600"
     preserveAspectRatio="xMidYMid meet">
"""

    # Iterate through the points and add a circle element for each
    for point in points:
        svg_content += f"""
  <circle cx="{point[0]}" cy="{point[1]}" r="{point_radius}"
          fill="black" stroke="none" />
"""

    # Close the SVG tag
    svg_content += """
</svg>
"""

    print("Writing SVG file...")
    # Write the complete SVG string to the output file
    with open(svg_file_path, "w") as f:
        f.write(svg_content)

    print(f"Successfully created SVG file: {svg_file_path}")


def vtp_to_svg(vtp_file_path: str, svg_file_path: str) -> tuple[float, list[tuple[float, float]]]:
    """
    Parses a VTP file and converts its points data to an SVG file,
    plotting only the points as circles.

    Args:
        vtp_file_path (str): The path to the input .vtp file.
        svg_file_path (str): The path for the output .svg file.
    """
    print(f"Reading VTP file from: {vtp_file_path}")

    # Create a VTK XML PolyData reader
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(vtp_file_path)
    reader.Update()

    # Get the polygonal data from the reader
    poly_data = reader.GetOutput()
    y_distance = get_dimensions(poly_data)[1]
    points = poly_data.GetPoints()

    num_points = points.GetNumberOfPoints()

    if num_points == 0:
        print("VTP file contains no points. No SVG will be generated.")
        return

    # Determine the bounding box to set the SVG viewBox
    bounds = poly_data.GetBounds()
    x_min, x_max, y_min, y_max = bounds[0], bounds[1], bounds[2], bounds[3]
    width = x_max - x_min
    height = y_max - y_min

    # Use padding to ensure points on the edge are visible
    padding = max(width, height) * 0.05
    viewBox_x = x_min - padding
    viewBox_y = y_min - padding
    viewBox_width = width + 2 * padding
    viewBox_height = height + 2 * padding

    # A small fixed radius for the points
    point_radius = max(width, height) * 0.005
    if point_radius == 0:
        point_radius = 1  # Fallback for single-point or zero-bound data

    print(f"Found {num_points} points.")
    svg_points = []

    # Start building the SVG content string
    # We use a viewBox to make the SVG scalable
    svg_content = f"""
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="{viewBox_x} {viewBox_y} {viewBox_width} {viewBox_height}"
     width="800" height="600"
     preserveAspectRatio="xMidYMid meet">
"""

    # Iterate through the points and add a circle element for each
    for i in range(num_points):
        point = points.GetPoint(i)
        svg_points.append(point)
        # VTK uses (x, y, z), but SVG is 2D, so we use (x, y)
        svg_content += f"""
  <circle cx="{point[0]}" cy="{point[1]}" r="{point_radius}"
          fill="black" stroke="none" />
"""

    # Close the SVG tag
    svg_content += """
</svg>
"""
    print("Writing SVG file...")
    # Write the complete SVG string to the output file
    with open(svg_file_path, "w") as f:
        f.write(svg_content)

    print(f"Successfully converted VTP to SVG. Output file: {svg_file_path}")
    return y_distance, svg_points


def intermediate_points_generation(points1, points2, weight):
    """
    Generates intermediate points between two sets of points based on a weight.

    Args:
        points1 (list): First set of points.
        points2 (list): Second set of points.
        weight (float): Weight for interpolation.

    Returns:
        list: List of interpolated points.
    """
    # points1 = smooothing(points1, iterations=10)
    # points2 = smooothing(points2, iterations=10)

    if (len(points1) < len(points2)):
        temp = points1
        points1 = points2
        points2 = temp

    if len(points1) == 0 or len(points2) == 0:
        print("One of the VTP files contains no points. No SVG will be generated.")
        return

    x1 = np.array([points1[i][0] for i in range(len(points1))])
    y1 = np.array([points1[i][1] for i in range(len(points1))])
    x2 = np.array([points2[i][0] if i < len(points2)
                  else points2[-1][0] for i in range(len(points1))])
    y2 = np.array([points2[i][1] if i < len(points2)
                  else points2[-1][1] for i in range(len(points1))])

    x3, y3 = fft_reconstruct.intermeidate_curve(x1, y1, x2, y2, weight)
    new_points = [(x3[i], y3[i]) for i in range(len(x3))]
    new_points = smooothing(new_points, iterations=10)
    return new_points


def intermediate_svg_generation(vtp_file_path_1, vtp_file_path_2, weight, svg_file_path):
    """
    Reads a VTP file and generates an SVG file with the points plotted as circles.

    Args:
        vtp_file_path (str): The path to the input .vtp file.
        svg_file_path (str): The path for the output .svg file.
    """

    points1 = get_vtp_points(vtp_file_path_1)
    points2 = get_vtp_points(vtp_file_path_2)

    new_points = intermediate_points_generation(points1, points2, weight)
    new_points = smooothing(new_points, iterations=10)
    points_to_svg(new_points, svg_file_path)


def smooothing(points, iterations=3):
    for _ in range(iterations):
        points_new = [(0.5*(points[i][0] + points[i+1][0]), 0.5 *
                       (points[i][1] + points[i+1][1])) for i in range(len(points) - 1)]
        points = points_new
    return points


def svg_generation(vtp_file_path, svg_file_path):

    points = get_vtp_points(vtp_file_path)
    x = np.array([points[i][0] for i in range(len(points))])
    y = np.array([points[i][1] for i in range(len(points))])
    freqs, coeffs, z = fft_reconstruct.fourier_curve_reconstruction(x, y)
    new_points = [(z[i].real, z[i].imag) for i in range(len(z) - 1)]
    new_points = smooothing(new_points, iterations=10)
    points_to_svg(new_points, svg_file_path)


def create_curve(p1, p2, p3, p4, w1, w2, svg_path):
    p5 = intermediate_points_generation(p1, p2, w1)
    p6 = intermediate_points_generation(p3, p4, w1)
    p7 = intermediate_points_generation(p5, p6, w2)
    points_to_svg(p7, svg_path)


if __name__ == "__main__":
    # svg_generation("run_7.vtp", "reconstructed_profile.svg")
    # intermediate_svg_generation(
    #     f"run_7.vtp", f"run_5.vtp", 0.5, "profile_intermediate.svg")
    p1 = get_vtp_points("images/run_5.vtp")
    p2 = get_vtp_points("images/run_7.vtp")
    create_curve(p1, p2, 0.1, "images/merged.svg")
