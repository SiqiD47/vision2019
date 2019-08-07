// *****************************************************************************
//
//
//
// *****************************************************************************

#pragma once

#include <stdio.h>
#include <vector>
#include "PvSystem.h"
#include "PvDeviceInfo.h"
#include "PvDevice.h"
#include "afxcmn.h"

// CIPConfiguration dialog

typedef struct _S_CAMERA_CONFIGURATION{
	CString	szModelName;
	CString	szMACAddress;
	CString	szIPAddress;
	CString	szSubnetMask;
	CString	szDefaultGateway;
}S_CAMERA_CONFIGURATION,*PS_CAMERA_CONFIGURATION;

class CIPConfiguration : public CDialog
{
	DECLARE_DYNAMIC(CIPConfiguration)

public:
	CIPConfiguration(CWnd* pParent = NULL);   // standard constructor
	virtual ~CIPConfiguration();


	std::vector<S_CAMERA_CONFIGURATION> mCameraConfig;


	void SearchCamera( INT iTimeout );
	void SetCameraTree(void);
	void SetCurrentInfomation(void);
	void CameraTreeApply(PBYTE pbyteIPAddress, PBYTE pbyteSubnetmask, PBYTE pbyteDefaultgateway );

	PvSystem mlSystem;
	int m_iDeviceCount;
	HTREEITEM hCurrentItem;

// Dialog Data
	enum { IDD = IDD_DIALOG_IPCONFIGURATION };

protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support

	DECLARE_MESSAGE_MAP()
public:
	afx_msg void OnBnClickedOk();
	afx_msg void OnBnClickedCancel();
	afx_msg void OnBnClickedButtonUp();
	CTreeCtrl mTreeDevice;
	afx_msg void OnTimer(UINT_PTR nIDEvent);
	virtual BOOL OnInitDialog();
	CIPAddressCtrl m_ipCurrentIPAddress;
	CIPAddressCtrl m_ipCurrentSubnetmask;
	CIPAddressCtrl m_ipCurrentDefaultgateway;
	afx_msg void OnNMClickTreeDevice(NMHDR *pNMHDR, LRESULT *pResult);
	afx_msg void OnTvnSelchangedTreeDevice(NMHDR *pNMHDR, LRESULT *pResult);
	CIPAddressCtrl m_ipNewIPAddress;
	CIPAddressCtrl m_ipNewSubnetmask;
	CIPAddressCtrl m_ipNewDefaultgateway;
	afx_msg void OnBnClickedButtonApply();
};
