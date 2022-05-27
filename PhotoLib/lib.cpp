#include "pch.h"
#include "Controller.h"

extern "C"
{

	__declspec(dllexport) Controller* createController()
	{
		return new Controller();
	}

	__declspec(dllexport) void destroyController(Controller* controller)
	{
		delete controller;
	}

	__declspec(dllexport) void saveDataFile(Controller* controller, const char* filename, unsigned short* images,
		int numTrials, int numPts, double intPts, int num_fp_pts, int width,
		int height, short * rliLow, short * rliHigh, short * rliMax,
		short sliceNo, short locNo, short recNo, int program, int intTrials)
	{

		controller->saveDataFile(filename, images, numTrials, numPts, intPts, num_fp_pts, width,
			height, rliLow, rliHigh, rliMax, sliceNo, locNo, recNo, program, intTrials);
	}


};