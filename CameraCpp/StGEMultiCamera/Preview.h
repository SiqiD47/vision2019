// *****************************************************************************
//
// 
//
// *****************************************************************************

#pragma once

#include <PvDisplayWnd.h>

// CPreview dialog

class CPreview : public CDialog
{
	DECLARE_DYNAMIC(CPreview)

public:
	CPreview(CWnd* pParent = NULL);   // standard constructor
	virtual ~CPreview();

	PvDisplayWnd mDisplay;

// Dialog Data
	enum { IDD = IDD_DIALOG_PREVIEW };

protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support

	DECLARE_MESSAGE_MAP()
public:
	afx_msg void OnSize(UINT nType, int cx, int cy);
};
