import cv2
import time
import numpy as np
from pathlib import Path

class Capture:
    """
    # Capture class used for storing recordings
    Exculsively created by the stereo object

    Holds a list of keypoint frames of form:
            timestep:1   timestep: 2
    list: [np.array([keypointIDX][3]), np.array([])]
    """
    def __init__(self):
        # Create capture directory
        # Read largest capture ID
        # Create new folder for this capture
        pass
    
    def computePose(self):
        # Saves 3D 
        pass
    

class Camera:
    def __init__(self, ID: int):
        """
        (int) ID: hardware ID of camera
        """

        self.ID = ID
        self.calibrated = False
        self.mtx = None
        self.dist = None
        self.cap = cv2.VideoCapture(self.ID, cv2.CAP_MSMF)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 120)
        time.sleep(1)

        if not self.cap.isOpened():
            raise Exception(f"Camera {self.ID} failed to start a capture.")
        else:
            print(f"Started capture on camera {ID}.")

    def get_cap(self):
        """
        returns: cv2 capture object associated with the camera.
        """
        return self.cap
    
    def get_mtx(self):
        if self.calibrated:
            return self.mtx
        else:
            raise Exception(f"Camera {self.ID} is not calibrated")
    
    def get_dist(self):
        if self.calibrated:
            return self.dist
        else:
            raise Exception(f"Camera {self.ID} is not calibrated")

    def take_pics(self, n:int, save_dir:str):
        """
        Press p to save an image
        (int) n: number of pictures to take
        (str) save_dir: relitive save directory
        returns: None
        """

        savedImgIdx = 0
        while savedImgIdx < n:
            ret, frame = self.cap.read()
            print(frame.shape)

            if not ret:
                raise Exception(f"Image grab failed in camera {self.ID}")

            grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cv2.imshow("Webcam", grayscale)

            if cv2.waitKey(1) & 0xFF == ord('p'):
                cv2.imwrite(f"{save_dir}/img{savedImgIdx}.jpg", grayscale)
                savedImgIdx += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
    def take_pics_timer(self, n:int, timer:int, save_dir:str):
        """
        (int) n: number of pictures to take
        (int) timer: number of seconds between each image capture
        (str) save_dir: relitive save directory
        returns: None
        """
        
        savedImgIdx = 0
        start = time.time_ns()

        while savedImgIdx < n:
            ret, frame = self.cap.read()

            if not ret:
                raise Exception(f"Image grab failed in camera {self.ID}")

            grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cv2.imshow("Webcam", grayscale)

    
            if (time.time_ns() - start) // 1e9 >= timer:
                print(f"CHEESE! {savedImgIdx}")
                cv2.imwrite(f"{save_dir}/img{savedImgIdx}.jpg", grayscale)
                savedImgIdx += 1
                start = time.time_ns()

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    def read(self):
        ret, frame = self.cap.read()
        if not ret:
            raise Exception(f"Failed to read camera {self.ID}")
        return frame

    def calibrate(self, check_pattern_size:tuple[int, int], img_dir:str, img_num:int, verify_corners:bool=False):
        """
        parameters:
            (tuple[int, int]) check_pattern_size: rows x cols of checkerboard intersections
            (str) img_dir: image directory to look for checkerboard images in
            (int) img_num: number of images in directiory
            (verify_corners): display the corners for verification? advance with q.
        returns:
            (float) ret: mean squared error between estimated pixel position and actual pixel position
            (np.array 3x3) camera_mtx: intrinsic camera matrix of the camera not including distortion coefficents
            (np.array) dist: distortion coefficents of lens
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

        img = None
        for i in range(img_num):
            img = cv2.imread(f"{img_dir}/img{i}.jpg", flags = cv2.IMREAD_GRAYSCALE + cv2.IMREAD_IGNORE_ORIENTATION)

            # find chessboard corners
            # corners starts from the bottom left and works up
            ret, corners = cv2.findChessboardCorners(img, check_pattern_size, None)
            corners = cv2.cornerSubPix(img, corners, search_win_size, zero_zone, criteria)

            if verify_corners:
                # DISPLAY CORNERS
                cv2.drawChessboardCorners(img, check_pattern_size, corners, ret)
                print(i)     
                cv2.imshow("See cmd line for num", img)
                while True:
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                cv2.destroyAllWindows()
            
            

            if ret:
                image_points.append(corners.astype(np.float32))
                object_points.append(object_point_grid[:len(corners)].astype(np.float32))

        if img is not None:
            ret, camera_matrix, dist, rvecs, tvecs = cv2.calibrateCamera(
                object_points,
                image_points,
                (img.shape[1], img.shape[0]),
                camera_matrix,
                dist_coeffs,
            )
            self.calibrated = True
            self.dist = dist
            self.mtx = camera_matrix
            return ret, camera_matrix, dist
        else:
            return None, None, None

    
class Stereo:
    def __init__(self, leftCam:Camera, rightCam:Camera):
        """
        left and right are determined as viewed in the binocular direction of the cameras
        """
        self.leftCam = leftCam
        self.rightCam = rightCam

        self.calibrated = False
        self.R = None
        self.T = None
    
    def take_pics(self, n:int, left_save_dir:str, right_save_dir:str):
        savedImgIdx = 0
        while savedImgIdx < n:
            retR, frameR = self.leftCam.cap.read()
            retL, frameL = self.leftCam.cap.read()

            if not retR or not retL:
                raise Exception("Stereo vision failed to initialize either or both cameras.")

            cv2.imshow("Right Camera", frameR)
            cv2.imshow("Left Camera", frameL)

            if cv2.waitKey(1) & 0xFF == ord('p'):
                cv2.imwrite(f"{left_save_dir}/img{savedImgIdx}.jpg", frameL)
                cv2.imwrite(f"{right_save_dir}/img{savedImgIdx}.jpg", frameR)
                savedImgIdx += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
 
    def take_pics_timer(self, n:int, timer:int, left_save_dir:str, right_save_dir:str):
        savedImgIdx = 0
        start = time.time_ns()

        while savedImgIdx < n:
            retR, frameR = self.rightCam.get_cap().read()
            retL, frameL = self.leftCam.get_cap().read()

            if not retR or not retL:
                print("capture failed to initialize")
                quit()

            cv2.imshow("Right Camera", frameR)
            cv2.imshow("Left Camera", frameL)

            if (time.time_ns() - start) // 1e9 >= timer:
                print(f"CHEESE! {savedImgIdx}")
                cv2.imwrite(f"{left_save_dir}/img{savedImgIdx}.jpg", frameL)
                cv2.imwrite(f"{right_save_dir}/img{savedImgIdx}.jpg", frameR)
                savedImgIdx += 1
                start = time.time_ns()

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def calibrate(self, check_pattern_size:tuple[int, int], square_size:float, left_img_dir:str, right_img_dir:str, img_num:int, verify_corners:bool=False):
        # FIND CHECKERBOARD CORNERS
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        conv_size = (11, 11)
        object_point_grid = np.zeros((check_pattern_size[0] * check_pattern_size[1], 3), dtype=np.float32)
        object_point_grid[:, :2] = np.mgrid[0:check_pattern_size[0], 0:check_pattern_size[1]].T.reshape(-1, 2)
        object_point_grid[:, [0, 1]] = object_point_grid[:, [1, 0]]


        imgPointsL = []
        imgPointsR = []
        object_points = []

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

                if verify_corners:
                    print(i)
                    cv2.drawChessboardCorners(imgR, check_pattern_size, cornersR, retR)
                    cv2.drawChessboardCorners(imgL, check_pattern_size, cornersL, retL)
                    
                    cv2.imshow("right", imgR)
                    k = cv2.waitKey(2000)
                    cv2.imshow("left", imgL)
                    k = cv2.waitKey(2000)
                
                object_points.append(object_point_grid)
                imgPointsR.append(cornersR)
                imgPointsL.append(cornersL)
        
        leftMtx = self.leftCam.get_mtx()
        rightMtx = self.rightCam.get_mtx()
        leftDist = self.leftCam.get_dist()
        rightDist = self.rightCam.get_dist()

        stereoRet, CM1, dist1, CM2, dist2, R, T, E, F = cv2.stereoCalibrate(
        object_points, imgPointsL, imgPointsR,
        leftMtx, leftDist, rightMtx, rightDist, # type: ignore
        (imgRGray.shape[1], imgRGray.shape[0]), criteria=criteria, flags=cv2.CALIB_FIX_INTRINSIC) # type: ignore
        print(f"Stereo Calibration Error: {stereoRet}")

        self.calibrated = True
        self.R = R
        self.T = T
        return R, T

    def display(self):
        while True:
            retR, frameR = self.rightCam.cap.read()
            retL, frameL = self.leftCam.cap.read()


            if not retR or not retL:
                print("capture failed to initialize")
                quit()

            cv2.imshow("Right Camera", frameR)
            cv2.imshow("Left Camera", frameL)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    def read(self):
        return self.leftCam.read(), self.rightCam.read()

    def triangulate(self, leftPoints, rightPoints):
        
        if not self.calibrated:
            raise Exception("Stereo system is not calibrated.")
        
        # setup projection matrcies in
        PL = np.hstack((np.eye(3), np.zeros((3,1)))) # using left camera as (0, 0)
        # R and T represent the rotation and translation relitive to the left camera
        PR = np.hstack((self.R, self.T)) # type: ignore

        # removes the distortion coefficents and intrinsic matrix
        leftPoints = np.array(leftPoints, dtype=np.float32)
        leftPoints = leftPoints.reshape(-1, 1, 2)
        rightPoints = np.array(rightPoints, dtype=np.float32)
        rightPoints = rightPoints.reshape(-1, 1, 2)

        leftUnwarped = cv2.undistortPoints(leftPoints, self.leftCam.get_mtx(), self.leftCam.get_dist())
        rightUnwarped = cv2.undistortPoints(rightPoints, self.rightCam.get_mtx(), self.rightCam.get_dist()) #type: ignore
        X_homogenous = cv2.triangulatePoints(PL, PR, leftUnwarped, rightUnwarped)
        X_real = X_homogenous[:3] / X_homogenous[3]
        print(f"X_real shape: {X_real.shape}")
        return X_real
