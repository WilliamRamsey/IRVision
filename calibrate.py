import cv2
import numpy as np
import time
from scipy import linalg


def take_pics(n: int, save_dir: str, cam_id: int = 1) -> None:
    cap = cv2.VideoCapture(cam_id, cv2.CAP_MSMF)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 120) 
    time.sleep(1)

    print("cap started")
    if not cap.isOpened():
        print("capture failed to open")
        quit()

    savedImgIdx = 0

    while savedImgIdx < n:
        ret, frame = cap.read()
        print(frame.shape)

        if not ret:
            print("capture failed to initialize")
            quit()
        grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow("Webcam", grayscale)

        if cv2.waitKey(1) & 0xFF == ord('p'):
            cv2.imwrite(f"{save_dir}/img{savedImgIdx}.jpg", grayscale)
            savedImgIdx += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    cap.release()
    cv2.destroyAllWindows()

def take_stereo_pics(n: int, left_cam_id: int, right_cam_id: int,
                     left_save_dir: str, right_save_dir: str):
    capR = cv2.VideoCapture(right_cam_id, cv2.CAP_MSMF)
    capR.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    capR.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    capR.set(cv2.CAP_PROP_FPS, 120) 
    time.sleep(1)

    capL = cv2.VideoCapture(left_cam_id, cv2.CAP_MSMF)
    capL.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    capL.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    capL.set(cv2.CAP_PROP_FPS, 120)

    if not capL.isOpened() or not capR.isOpened():
        print("capture failed to open")
        quit()


    savedImgIdx = 0
    while savedImgIdx < n:
        retR, frameR = capR.read()
        retL, frameL = capL.read()

        if not retR or not retL:
            print("capture failed to initialize")
            quit()

        cv2.imshow("Right Camera", frameR)
        cv2.imshow("Left Camera", frameL)

        if cv2.waitKey(1) & 0xFF == ord('p'):
            cv2.imwrite(f"{left_save_dir}/img{savedImgIdx}.jpg", frameL)
            cv2.imwrite(f"{right_save_dir}/img{savedImgIdx}.jpg", frameR)
            savedImgIdx += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capR.release()
    capL.release()
    cv2.destroyAllWindows()

def calibrate_cam(check_pattern_size: tuple[int, int], img_dir: str, img_num: int):
    """
    
    """

    # SUBPIX CRITERIA
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    search_win_size = (11, 11)
    zero_zone = (-1, -1)

    # Lists for object and image points
    object_points = []
    image_points = []
    object_point_grid = np.zeros((check_pattern_size[0] * check_pattern_size[1], 3), dtype=np.float64)
    object_point_grid[:, :2] = np.mgrid[0:check_pattern_size[0], 0:check_pattern_size[1]].T.reshape(-1, 2)
    object_point_grid[:, [0, 1]] = object_point_grid[:, [1, 0]]

    # initial camera matrix and distortion coefficent guess
    camera_matrix = np.eye(3, dtype=np.float64)
    dist_coeffs = np.zeros((5, 1), dtype=np.float64)


    for i in range(img_num):
        img = cv2.imread(f"{img_dir}/img{i}.jpg", flags = cv2.IMREAD_GRAYSCALE + cv2.IMREAD_IGNORE_ORIENTATION)

        # find chessboard corners
        # corners starts from the bottom left and works up
        ret, corners = cv2.findChessboardCorners(img, check_pattern_size, None)
        corners = cv2.cornerSubPix(img, corners, search_win_size, zero_zone, criteria)

        """
        # DISPLAY CORNERS
        for corner in corners:
            cv2.circle(img, [int(px) for px in corner[0]], 5, (0, 0, 0), -1)
            print(corner[0])
        

            cv2.imshow(f"{i}", img)
            while True:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        cv2.destroyAllWindows()
        """

        if ret:
            image_points.append(corners.astype(np.float32))
            object_points.append(object_point_grid[:len(corners)].astype(np.float32))

    ret, camera_matrix, dist, rvecs, tvecs = cv2.calibrateCamera(
        object_points,
        image_points,
        img.shape[::-1],
        camera_matrix,
        dist_coeffs,
    )


    return ret, camera_matrix, dist


    
    """
    dstimg = cv2.imread("leftCamCal/img15.jpg")
    undistorted = cv2.undistort(dstimg, camera_matrix, dist, None)
    cv2.imshow("undistorted", undistorted)

    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    

    cv2.destroyAllWindows()
    """

def calibrate_stereo(check_pattern_size:tuple[int, int], square_size:float,
                     left_img_dir: str, right_img_dir: str,
                     left_internals:dict, right_internals:dict,
                     img_num:int):
    """
    check
    """
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    conv_size = (11, 11)

    # undistort images from cam1 with it's matrix
    # undistort images from cam2 with it's matrix
    # find corners of checkerboard in each image
    object_point_grid = np.zeros((check_pattern_size[0] * check_pattern_size[1], 3), dtype=np.float32)
    object_point_grid[:, :2] = np.mgrid[0:check_pattern_size[0], 0:check_pattern_size[1]].T.reshape(-1, 2)
    object_point_grid[:, [0, 1]] = object_point_grid[:, [1, 0]]


    imgPointsL = []
    imgPointsR = []
    object_points = []

    stereocal_flags = cv2.CALIB_FIX_INTRINSIC

    for i in range(img_num):
        imgR = cv2.imread(f"{right_img_dir}/img{i}.jpg")
        imgL = cv2.imread(f"{left_img_dir}/img{i}.jpg")

        imgRGray = cv2.cvtColor(imgR, cv2.COLOR_BGR2GRAY)
        imgLGray = cv2.cvtColor(imgL, cv2.COLOR_BGR2GRAY)

        retR, cornersR = cv2.findChessboardCorners(imgRGray, check_pattern_size, None)
        retL, cornersL = cv2.findChessboardCorners(imgLGray, check_pattern_size, None)
        if retR and retL:
            cornersR = cv2.cornerSubPix(imgRGray, cornersR, conv_size, (-1, -1), criteria)
            cornersL = cv2.cornerSubPix(imgLGray, cornersL, conv_size, (-1, -1), criteria)

            """
            cv2.drawChessboardCorners(imgR, check_pattern_size, cornersR, retR)
            cv2.drawChessboardCorners(imgL, check_pattern_size, cornersL, retL)
            
            cv2.imshow("right", imgR)
            k = cv2.waitKey(2000)
            cv2.imshow("left", imgL)
            k = cv2.waitKey(2000)
            """


            object_points.append(object_point_grid)
            imgPointsR.append(cornersR)
            imgPointsL.append(cornersL)



        else:
            print(f"Chalking {i}")
        
    stereoRet, CM1, dist1, CM2, dist2, R, T, E, F = cv2.stereoCalibrate(
            object_points, imgPointsL, imgPointsR,
            left_internals["mtx"], left_internals["dst"], right_internals["mtx"], right_internals["dst"],
            (imgRGray.shape[1], imgRGray.shape[0]), criteria=criteria, flags=stereocal_flags)

    return R, T

def find_light(right_cam_id:int, left_cam_id:int):
    """
    Returns:
    left_image_cords
    right_image_cord
    """
    capR = cv2.VideoCapture(right_cam_id, cv2.CAP_MSMF)
    capR.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    capR.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    capR.set(cv2.CAP_PROP_FPS, 120) 
    time.sleep(1)

    capL = cv2.VideoCapture(left_cam_id, cv2.CAP_MSMF)
    capL.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    capL.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    capL.set(cv2.CAP_PROP_FPS, 120)

    if not capL.isOpened() or not capR.isOpened():
        print("capture failed to open")
        return None, None

    leftImgCords = []
    rightImgCords = []

    lightEmUp = False

    while True:
        retR, frameR = capR.read()
        retL, frameL = capL.read()

        grayscaleR = cv2.cvtColor(frameR, cv2.COLOR_BGR2GRAY)
        grayscaleL = cv2.cvtColor(frameL, cv2.COLOR_BGR2GRAY)
        retval, thresholdR = cv2.threshold(grayscaleR, 200, 225, cv2.THRESH_BINARY)
        retval, thresholdL = cv2.threshold(grayscaleL, 200, 225, cv2.THRESH_BINARY)

        # cv2.imshow("Right Camera", thresholdR)
        # cv2.imshow("Left Camera", thresholdL)

        # grab glob coordinates from left and right frame.
        num_labelsR, labelsR, statsR, centroidsR = cv2.connectedComponentsWithStats(
            thresholdR,
            connectivity=8
        )
        num_labelsL, labelsL, statsL, centroidsL = cv2.connectedComponentsWithStats(
            thresholdL,
            connectivity=8
        )

        key = cv2.waitKey(5) & 0xFF

        if len(centroidsL) > 1 and len(centroidsR) > 1: # make sure we actually find  centroid
            
            largestBlobIdxR = 1 + np.argmax(statsR[:, cv2.CC_STAT_AREA][1:])
            largestBlobIdxL = 1 + np.argmax(statsL[:, cv2.CC_STAT_AREA][1:])
                
            cv2.circle(frameL, centroidsL[largestBlobIdxL].astype(int), 5, (225,0,0), -1)
            cv2.circle(frameR, centroidsR[largestBlobIdxR].astype(int), 5, (225,0,0), -1)
            cv2.imshow("left", frameL)
            cv2.imshow("right", frameR)
            
            if key == ord('s'):
                lightEmUp = True
            elif key == ord('q'):
                capL.release()
                capR.release()
                cv2.destroyAllWindows()
                return leftImgCords, rightImgCords

            if lightEmUp:
                leftImgCords.append(centroidsL[largestBlobIdxL])
                rightImgCords.append(centroidsR[largestBlobIdxR])




def triangulate(leftPoints, rightPoints, leftIntrinsics, rightIntrinsics, R, T):
    # setup projection matrcies in
    PL = np.hstack((np.eye(3), np.zeros((3,1)))) # using left camera as (0, 0)
    # R and T represent the rotation and translation relitive to the left camera
    PR = np.hstack((R, T))

    # removes the distortion coefficents and intrinsic matrix
    leftPoints = np.array(leftPoints, dtype=np.float32)
    leftPoints = leftPoints.reshape(-1, 1, 2)
    rightPoints = np.array(rightPoints, dtype=np.float32)
    rightPoints = rightPoints.reshape(-1, 1, 2)
    leftUnwarped = cv2.undistortPoints(leftPoints, leftIntrinsics["mtx"], leftIntrinsics["dst"])
    rightUnwarped = cv2.undistortPoints(rightPoints, rightIntrinsics["mtx"], rightIntrinsics["dst"])
    X_homogenous = cv2.triangulatePoints(PL, PR, leftUnwarped, rightUnwarped)
    X_real = X_homogenous[:3] / X_homogenous[3]
    print(X_real)
    return X_real