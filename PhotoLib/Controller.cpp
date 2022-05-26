//=============================================================================
// Controller.cpp
//=============================================================================
#include "pch.h"

#include <iostream>
#include <stdlib.h>		// _gcvt()
#include <fstream>
#include <time.h>
#include <string.h>
#include <stdio.h>
#include <exception>
#include <stdint.h>
#include <omp.h>
#include <unordered_map>

#include "Controller.h"

// #pragma comment(lib,".\\lib\\NIDAQmx.lib")  Chun suggested it but turns out not to make any difference
using namespace std;

 //=============================================================================
Controller::Controller()
{
}


//=============================================================================
Controller::~Controller()
{
}

int Controller::saveDataFile(unsigned short * images, int numTrials, int numPts, double intPts,
	int num_fp_pts, int width,
	int height, short * rliLow, short * rliHigh, short * rliMax,
	short sliceNo, short locNo, short recNo, int program, int intTrials)
{
	const char *fileName = "output.zda";
	short*** raw_data = (short***)images;
	fstream file;
	file.open(fileName, ios::out | ios::binary | ios::trunc);

	saveRecControl(&file, sliceNo, locNo, recNo, program, numTrials, intTrials, numPts, intPts, width, height);
	saveData(&file, raw_data, numTrials, numPts, num_fp_pts, width, height, rliLow, rliHigh, rliMax);

	file.close();

	//
	return 1;
}

//=============================================================================
void Controller::saveRecControl(fstream *file, short sliceNo, short locNo, short recNo, int program, int numTrials, int intTrials, int numPts, double intPts, int width, int height)
{
	char chBuf;
	short shBuf;
	int nBuf;
	float fBuf;
	time_t tBuf;
	int chSize = sizeof(char);
	int shSize = sizeof(short);
	int nSize = sizeof(int);
	int fSize = sizeof(float);
	int tSize = sizeof(time_t);

	// Version
	chBuf = 5;
	file->write((char*)&chBuf, chSize);

	// Slice Number
	shBuf = sliceNo;
	file->write((char*)&shBuf, shSize);

	// Location Number
	shBuf = locNo;
	file->write((char*)&shBuf, shSize);

	// Record Number
	shBuf = recNo;
	file->write((char*)&shBuf, shSize);

	// Camera Program
	nBuf = program;
	file->write((char*)&nBuf, nSize);

	// Number of Trials
	chBuf = char(numTrials);
	file->write((char*)&chBuf, chSize);

	// Interval between Trials
	chBuf = char(intTrials);
	file->write((char*)&chBuf, chSize);

	// Acquisition Gain
	shBuf = 1;
	file->write((char*)&shBuf, shSize);

	// Number of Points per Trace
	nBuf = numPts;
	file->write((char*)&nBuf, nSize);

	// Time - RecControl
	tBuf = (time_t)1;
	file->write((char*)&tBuf, tSize);

	// Reset Onset
	fBuf = 0;
	file->write((char*)&fBuf, fSize);

	// Reset Duration
	fBuf = 0;
	file->write((char*)&fBuf, fSize);

	// Shutter Onset
	fBuf = 0;
	file->write((char*)&fBuf, fSize);

	// Shutter Duration
	fBuf = 1000;
	file->write((char*)&fBuf, fSize);

	// Stimulation 1 Onset
	fBuf = 100;
	file->write((char*)&fBuf, fSize);

	// Stimulation 1 Duration
	fBuf = 1;
	file->write((char*)&fBuf, fSize);

	// Stimulation 2 Onset
	fBuf = 0;
	file->write((char*)&fBuf, fSize);

	// Stimulation 2 Duration
	fBuf = 0;
	file->write((char*)&fBuf, fSize);

	// Acquisition Onset
	fBuf = 0;
	file->write((char*)&fBuf, fSize);

	// Interval between Samples
	fBuf = float(intPts);
	file->write((char*)&fBuf, fSize);

	// Array Dimensions
	nBuf = width;
	file->write((char*)&nBuf, nSize);
	nBuf = height;
	file->write((char*)&nBuf, nSize);

	// depth set at a constant 2 bytes (hopefully) otherwise there is trouble
	nBuf = 2;
	file->write((char*)&nBuf, nSize);
}

//=============================================================================
void Controller::saveData(fstream * file, short *** images, int numTrials, int numPts, int num_fp_pts, int width, int height, short * rliLow, short * rliHigh, short * rliMax)
{
	int i, j;
	short shBuf;
	int shSize = sizeof(short);
	int arr_diodes = width * height + num_fp_pts;

	file->seekg(1024);

	// RLI
	short* ptr = rliLow;
	for (i = 0; i < arr_diodes; i++)
	{
		file->write((char*)ptr, shSize);
		ptr++;
	}

	ptr = rliHigh;
	for (i = 0; i < arr_diodes; i++)
	{
		file->write((char*)ptr, shSize);
		ptr++;
	}

	ptr = rliHigh;
	for (i = 0; i < arr_diodes; i++)
	{
		file->write((char*)ptr, shSize);
		ptr++;
	}

	// Load Raw Data
	int dataSize = shSize * numPts;

	for (i = 0; i < numTrials; i++)
	{
		for (j = 0; j < arr_diodes; j++)
		{
			file->write((const char*)images[i][j], dataSize);
		}
	}
}