// *****************************************************************************
//
// 
//
// *****************************************************************************

#pragma once

#include <PvDisplayWnd.h>
#include <PvBuffer.h>
#include <PvDevice.h>
#include <PvPipeline.h>

class Thread
{
public:
	Thread( PvDisplayWnd *aDisplayWnd, PvDevice *aDevice, PvPipeline *aPipeline );
	~Thread(void);

	void Start();
	void Stop();

	void SetPriority( int aPriority );
	int GetPriority() const;

	bool IsDone();
	DWORD GetReturnValue();

protected:

	static unsigned long WINAPI Link( void *aParam );
	virtual DWORD Function();

	bool IsStopping() const;

private:

	HANDLE mHandle;
	DWORD mID;

	bool mStop;

	DWORD mReturnValue;

	PvDisplayWnd *mDisplayWnd;
	PvDevice *mDevice;
	PvPipeline *mPipeline;
};
