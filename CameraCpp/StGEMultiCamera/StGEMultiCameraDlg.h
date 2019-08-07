// *****************************************************************************
//
// 
//
// *****************************************************************************

// StGEMultiCameraDlg.h : header file
//

#pragma once
#include "Resource.h"

#include "afxcmn.h"
#include "afxwin.h"

#include "IPConfiguration.h"
#include "Thread.h"
#include "Preview.h"
#include <PvDevice.h>
#include <PvGenParameter.h>
#include <PvStream.h>
#include <PvPipeline.h>
#include <PvSystem.h>
#include <PvBufferWriter.h>


class CDeviceInfo : public PvGenEventSink, PvDeviceEventSink
{
public:
	CDeviceInfo()
		:mPipeline(&mStream)
	{
	};
	~CDeviceInfo()
	{

	};

	PvDevice mDevice;
    PvStream mStream;
    PvPipeline mPipeline;

	Thread *mThreadDisplay;
	CPreview *mPreview;

	PvString mIPAddress;
	PvString mMACAddress;
	PvString mModelName;
	int mID;

protected:

	void OnParameterUpdate( PvGenParameter *aParameter ){

		PvString lName;
		if ( !aParameter->GetName( lName ).IsOK() )
		{
			return;
		}
	};
};

// CStGEMultiCameraDlg dialog
class CStGEMultiCameraDlg : public CDialog
{
// Construction
public:
	CStGEMultiCameraDlg(CWnd* pParent = NULL);	// standard constructor

	CIPConfiguration mIPConfiguration;

	std::vector<CDeviceInfo*> mpDeviceInfo;
	INT hAutoSelectCamera( PvSystem *plSystem, int iTimeout, HANDLE *pHandle, int iHandleSize );
	BOOL Connect( PvDeviceInfo *aDI );
	void Disconnect(CDeviceInfo *pDeviceInfo);

	void StartStreaming(CDeviceInfo *pDeviceInfo);
	void StopStreaming(CDeviceInfo *pDeviceInfo);

	void StartAcquisition(CDeviceInfo *pDeviceInfo);
	void StopAcquisition(CDeviceInfo *pDeviceInfo);

    bool IsAcquiringImages() const { return mAcquiringImages; }
	void SetCameraTree();
	void EnableInterface();

// Dialog Data
	enum { IDD = IDD_STGEMULTICAMERA_DIALOG };

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support


// Implementation
protected:
	HICON m_hIcon;

	// Generated message map functions
	virtual BOOL OnInitDialog();
	afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	DECLARE_MESSAGE_MAP()

    bool mAcquiringImages;

public:
	afx_msg void OnBnClickedCancel();
	afx_msg void OnBnClickedButtonIpconfiguration();
	afx_msg void OnBnClickedButtonConnect();
	afx_msg void OnBnClickedButtonDisconnect();
	afx_msg void OnBnClickedButtonStart();
	afx_msg void OnBnClickedButtonStop();
	afx_msg void SaveImage(int, CString);
	afx_msg void GetImage(PvBuffer *, int);
	afx_msg void OnDestroy();
	CTreeCtrl mTreeConnectDevice;
	afx_msg void OnTvnSelchangedTreeConnectdevice(NMHDR *pNMHDR, LRESULT *pResult);
};
