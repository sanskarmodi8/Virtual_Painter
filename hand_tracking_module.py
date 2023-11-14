import cv2
import mediapipe as mp
import time
class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        
        # mode = False means static image
        self.mode = mode
        
        self.maxHands = maxHands
        
        # min confidence for detection
        self.detectionCon = detectionCon
        
        # min confidence for tracking
        self.trackCon = trackCon
        
        # mediapipe hands object
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,min_detection_confidence=self.detectionCon, min_tracking_confidence=self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        
    # this function will detect hands and draw landmarks on the hands
    def findHands(self, img, draw=True):
        # convert to RGB
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        
        
        if self.results.multi_hand_landmarks: # if hand is detected in the frame then draw landmarks for each hand detected and also draw connections between the landmarks
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,self.mpHands.HAND_CONNECTIONS)
        return img
    
    # this function will return the position of the landmarks
    def findPosition(self, img, handNo=0, draw=True):
        lmList = [] # list of landmark positions in the format [id, x, y]
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h) # we multiply by w and h because the landmark coordinates are normalized but we need pixel values
                lmList.append([id, cx, cy])
                # # draw circle for the tip of the index finger
                if draw and id==8:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
        return lmList
    
def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()
    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        if len(lmList) != 0:
            print("Tip of index finger :", lmList[8]) # print the position of the tip of the index finger # here, 4 specifies the index of the tip of the index finger
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)
        cv2.imshow("Image", img)
        cv2.waitKey(1)
        
if __name__ == "__main__":
    main()
