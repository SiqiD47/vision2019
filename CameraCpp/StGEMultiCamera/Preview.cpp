// *****************************************************************************
//
//
//
// *****************************************************************************
// Preview.cpp :
//

#include "stdafx.h"
#include "StGEMultiCamera.h"
#include "Preview.h"


// CPreview dialog

IMPLEMENT_DYNAMIC(CPreview, CDialog)

CPreview::CPreview(CWnd* pParent /*=NULL*/)
	: CDialog(CPreview::IDD, pParent)
{

}

CPreview::~CPreview()
{
}

void CPreview::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
}


BEGIN_MESSAGE_MAP(CPreview, CDialog)
	ON_WM_SIZE()
END_MESSAGE_MAP()


// ==========================================================================
void CPreview::OnSize(UINT nType, int cx, int cy)
{
	CDialog::OnSize(nType, cx, cy);

	RECT aRect;
	GetClientRect(&aRect);
	mDisplay.SetPosition( 0, 0, aRect.right-aRect.left, aRect.bottom-aRect.top );

}
