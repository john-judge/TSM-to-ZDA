#pragma once
//=============================================================================
// Controller.h
//=============================================================================
#ifndef _Controller_h
#define _Controller_h
//=============================================================================
#include <fstream>

//=============================================================================
class Controller
{

public:
	// Constructors
	Controller();
	~Controller();
	void saveDataFile(unsigned short * images, int numTrials, int numPts, double intPts, int num_fp_pts, int width, int height, short * rliLow, short * rliHigh, short * rliMax, short sliceNo, short locNo, short recNo, int program, int intTrials);
	void saveRecControl(std::fstream * file, short sliceNo, short locNo, short recNo, int program, int numTrials, int intTrials, int numPts, double intPts, int width, int height);
	void saveData(std::fstream *file, short* images, int numTrials, int numPts, int num_fp_pts, int width, int height, short* rliLow, short* rliHigh, short* rliMax);

};

//=============================================================================
#endif
//=============================================================================