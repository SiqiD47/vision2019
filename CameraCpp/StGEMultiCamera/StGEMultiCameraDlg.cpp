// *****************************************************************************
//
// 
//
// *****************************************************************************
// StGEMultiCameraDlg.cpp : implementation file
//

#include "stdafx.h"
#include "StGEMultiCamera.h"
#include "StGEMultiCameraDlg.h"
#include "atlimage.h"
#include "atlstr.h"
#include <string>


#ifdef _DEBUG
#define new DEBUG_NEW
#endif


// CAboutDlg dialog used for App About

class CAboutDlg : public CDialog
{
public:
	CAboutDlg();

// Dialog Data
	enum { IDD = IDD_ABOUTBOX };

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support

// Implementation
protected:
	DECLARE_MESSAGE_MAP()
};

CAboutDlg::CAboutDlg() : CDialog(CAboutDlg::IDD)
{
}

void CAboutDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
}

BEGIN_MESSAGE_MAP(CAboutDlg, CDialog)
END_MESSAGE_MAP()


// CStGEMultiCameraDlg dialog




CStGEMultiCameraDlg::CStGEMultiCameraDlg(CWnd* pParent /*=NULL*/)
	: CDialog(CStGEMultiCameraDlg::IDD, pParent)
{
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void CStGEMultiCameraDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	DDX_Control(pDX, IDC_TREE_CONNECTDEVICE, mTreeConnectDevice);
}

BEGIN_MESSAGE_MAP(CStGEMultiCameraDlg, CDialog)
	ON_WM_SYSCOMMAND()
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	//}}AFX_MSG_MAP
	ON_BN_CLICKED(IDCANCEL, &CStGEMultiCameraDlg::OnBnClickedCancel)
	ON_BN_CLICKED(IDC_BUTTON_IPCONFIGURATION, &CStGEMultiCameraDlg::OnBnClickedButtonIpconfiguration)
	ON_BN_CLICKED(IDC_BUTTON_CONNECT, &CStGEMultiCameraDlg::OnBnClickedButtonConnect)
	ON_BN_CLICKED(IDC_BUTTON_DISCONNECT, &CStGEMultiCameraDlg::OnBnClickedButtonDisconnect)
	ON_BN_CLICKED(IDC_BUTTON_START, &CStGEMultiCameraDlg::OnBnClickedButtonStart)
	ON_BN_CLICKED(IDC_BUTTON_STOP, &CStGEMultiCameraDlg::OnBnClickedButtonStop)
	ON_WM_DESTROY()
	ON_NOTIFY(TVN_SELCHANGED, IDC_TREE_CONNECTDEVICE, &CStGEMultiCameraDlg::OnTvnSelchangedTreeConnectdevice)
END_MESSAGE_MAP()


// CStGEMultiCameraDlg message handlers

BOOL CStGEMultiCameraDlg::OnInitDialog()
{
	CDialog::OnInitDialog();

	// Add "About..." menu item to system menu.

	// IDM_ABOUTBOX must be in the system command range.
	ASSERT((IDM_ABOUTBOX & 0xFFF0) == IDM_ABOUTBOX);
	ASSERT(IDM_ABOUTBOX < 0xF000);

	CMenu* pSysMenu = GetSystemMenu(FALSE);
	if (pSysMenu != NULL)
	{
		CString strAboutMenu;
		strAboutMenu.LoadString(IDS_ABOUTBOX);
		if (!strAboutMenu.IsEmpty())
		{
			pSysMenu->AppendMenu(MF_SEPARATOR);
			pSysMenu->AppendMenu(MF_STRING, IDM_ABOUTBOX, strAboutMenu);
		}
	}

	// Set the icon for this dialog.  The framework does this automatically
	//  when the application's main window is not a dialog
	SetIcon(m_hIcon, TRUE);			// Set big icon
	SetIcon(m_hIcon, FALSE);		// Set small icon

	// TODO: Add extra initialization here
	mAcquiringImages = false;

	return TRUE;  // return TRUE  unless you set the focus to a control
}

void CStGEMultiCameraDlg::OnSysCommand(UINT nID, LPARAM lParam)
{
	if ((nID & 0xFFF0) == IDM_ABOUTBOX)
	{
		CAboutDlg dlgAbout;
		dlgAbout.DoModal();
	}
	else
	{
		CDialog::OnSysCommand(nID, lParam);
	}
}

// If you add a minimize button to your dialog, you will need the code below
//  to draw the icon.  For MFC applications using the document/view model,
//  this is automatically done for you by the framework.

void CStGEMultiCameraDlg::OnPaint()
{
	if (IsIconic())
	{
		CPaintDC dc(this); // device context for painting

		SendMessage(WM_ICONERASEBKGND, reinterpret_cast<WPARAM>(dc.GetSafeHdc()), 0);

		// Center icon in client rectangle
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// Draw the icon
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialog::OnPaint();
	}
}

// The system calls this function to obtain the cursor to display while the user drags
//  the minimized window.
HCURSOR CStGEMultiCameraDlg::OnQueryDragIcon()
{
	return static_cast<HCURSOR>(m_hIcon);
}


void CStGEMultiCameraDlg::OnBnClickedCancel()
{
	OnCancel();
}

void CStGEMultiCameraDlg::OnBnClickedButtonIpconfiguration()
{
	mIPConfiguration.DoModal();
}

#ifdef __cplusplus
extern "C"
#endif
void CStGEMultiCameraDlg::OnBnClickedButtonConnect()
{
	PvSystem lSystem;
	HANDLE hCamera[10];
	int iSelectCamera=0;

	HCURSOR hCursor = ::SetCursor( ::LoadCursor(NULL, IDC_WAIT) );

	do{
		memset( hCamera,0,sizeof(hCamera) );
		iSelectCamera = hAutoSelectCamera( &lSystem, 2000, &hCamera[0], sizeof(hCamera)/sizeof(hCamera[0]) );
		for( int i=0; i<iSelectCamera; i++ ){
			Connect( (PvDeviceInfo *)hCamera[i] );
		}
	}while(iSelectCamera>=sizeof(hCamera)/sizeof(hCamera[0]));
	
	EnableInterface();

	SetCameraTree();

	hCursor = ::SetCursor( hCursor );
}

// =============================================================================
void CStGEMultiCameraDlg::OnBnClickedButtonDisconnect()
{
	while(mpDeviceInfo.size()>0){
		Disconnect(mpDeviceInfo[0]);
	};
	EnableInterface();

	SetCameraTree();
}

// =============================================================================
void CStGEMultiCameraDlg::OnBnClickedButtonStart()
{
	for (unsigned int z = 0; z < mpDeviceInfo.size(); z++) {
		if (mpDeviceInfo[z]->mDevice.IsConnected()) {
			StartAcquisition(mpDeviceInfo[z]);
			mpDeviceInfo[z]->mPreview->ShowWindow(SW_SHOW);
			mAcquiringImages = true;
		}
	}
	EnableInterface();
}

// =============================================================================
void CStGEMultiCameraDlg::SaveImage(int z, CString path) // z is used to specify a particular camera in the list
{
	// Save HWND as a bmp file
	HWND hwnd = mpDeviceInfo[z]->mPreview->GetSafeHwnd();
	HDC hDC = ::GetWindowDC(hwnd);
	RECT rect;
	::GetWindowRect(hwnd, &rect);
	HDC hDCMem = ::CreateCompatibleDC(hDC);
	HBITMAP hBitMap = ::CreateCompatibleBitmap(hDC, rect.right - rect.left, rect.bottom - rect.top);
	HBITMAP hOldMap = (HBITMAP)::SelectObject(hDCMem, hBitMap);
	::BitBlt(hDCMem, 0, 0, rect.right - rect.left, rect.bottom - rect.top, hDC, 0, 0, SRCCOPY);
	CImage image;
	image.Attach(hBitMap);
	image.Save(path);
	image.Detach();
	::SelectObject(hDCMem, hOldMap);
	::DeleteObject(hBitMap);
	::DeleteDC(hDCMem);
	::DeleteDC(hDC);
}

void CStGEMultiCameraDlg::GetImage(PvBuffer *lBuffer, int ip) // z is used to specify a particular camera in the list
{
	CString lExt;
	PvBufferFormatType lType;

	lExt = _T(".bmp");
	lType = PvBufferFormatBMP;

	wchar_t lFileName[MAX_PATH];
	
	int i = 2; // file index
	if(ip == 2) // 192.168.2.2, right
		swprintf_s(lFileName, MAX_PATH, L"C:\\Users\\CNAMZHU1\\Desktop\\vision2019\\experiment\\Hongqi\\car_right\\%d.bmp", i);
	else if (ip == 3) // 192.168.2.3, left2
		swprintf_s(lFileName, MAX_PATH, L"C:\\Users\\CNAMZHU1\\Desktop\\vision2019\\experiment\\Hongqi\\car_left2\\%d.bmp", i);
	else if (ip == 4) // 192.168.2.4, left
		swprintf_s(lFileName, MAX_PATH, L"C:\\Users\\CNAMZHU1\\Desktop\\vision2019\\experiment\\Hongqi\\car_left\\%d.bmp", i);
	else // 192.168.2.5, right2
		swprintf_s(lFileName, MAX_PATH, L"C:\\Users\\CNAMZHU1\\Desktop\\vision2019\\experiment\\Hongqi\\car_right2\\%d.bmp", i);

	//mFilteringDlg->ConfigureConverter(mBufferWriter.GetConverter());
	PvBufferWriter mBufferWriter;
	mBufferWriter.Store(lBuffer, lFileName, lType);
}


// =============================================================================
void CStGEMultiCameraDlg::OnBnClickedButtonStop()
{	
	for(;;){
		for( unsigned int z = 0; z < mpDeviceInfo.size(); z++ ){
			if ( mpDeviceInfo[z]->mDevice.IsConnected() ){
				PvBuffer *lBuffer = NULL;
				PvResult  lOperationResult;
				// Try retrieving a buffer, using default timeout
				CDeviceInfo *device = mpDeviceInfo[z];
				PvResult lResult = device->mPipeline.RetrieveNextBuffer(&lBuffer, 0xFFFFFFFF, &lOperationResult);
				if (lResult.IsOK())
				{
					if (mpDeviceInfo[z]->mIPAddress == "169.254.2.2") {
						GetImage(lBuffer, 2);
					}
					else if (mpDeviceInfo[z]->mIPAddress == "169.254.2.3") {
						GetImage(lBuffer, 3);
					}
					else if (mpDeviceInfo[z]->mIPAddress == "169.254.2.4") {
						GetImage(lBuffer, 4);
					}
					else { // if (mpDeviceInfo[z]->mIPAddress == "169.254.2.5")
						GetImage(lBuffer, 5);
					}
					// Release buffer back to the pipeline
					device->mPipeline.ReleaseBuffer(lBuffer);
				}
				else {
					device->mPipeline.ReleaseBuffer(lBuffer);
				}
				mpDeviceInfo[z]->mPreview->CloseWindow(); // close the window
			}
		}
		Sleep(1000); // wait for 1s and re-save the image
		EnableInterface();
	}
}

// =============================================================================
INT CStGEMultiCameraDlg::hAutoSelectCamera( PvSystem *plSystem, int iTimeout, HANDLE *pHandle, int iHandleSize )
{
	int iCamCount = 0;
	PvResult pvResult;
	PvDeviceInfo *lDeviceInfo = NULL;

	plSystem->SetDetectionTimeout( iTimeout );
	pvResult = plSystem->Find();
	if( pvResult.IsOK() )
	{
		PvUInt32 lInterfaceCount = plSystem->GetInterfaceCount();

		for( PvUInt32 x = 0; x < lInterfaceCount; x++ )
		{
			// get pointer to each of interface
			PvInterface * lInterface = plSystem->GetInterface( x );

			// Get the number of GEV devices that were found using GetDeviceCount.
			PvUInt32 lDeviceCount = lInterface->GetDeviceCount();

			for( PvUInt32 y = 0; y < lDeviceCount ; y++ )
			{
				lDeviceInfo = lInterface->GetDeviceInfo( y );
				if( lDeviceInfo->GetAccessStatus()==PvAccessOpen ){
					pHandle[iCamCount++] = (HANDLE)lDeviceInfo;
					if( iCamCount>=iHandleSize )
						break;
				}
			}
			if( iCamCount>=iHandleSize )
				break;
		}
	}
	return iCamCount;
}

// =============================================================================
BOOL CStGEMultiCameraDlg::Connect( PvDeviceInfo *aDI )
{
	ASSERT( aDI != NULL );
	if ( aDI == NULL )	
    {
		return FALSE;
	}
	CDeviceInfo *pDeviceInfo = new CDeviceInfo;

	mpDeviceInfo.push_back(pDeviceInfo);
	pDeviceInfo->mID = (int)mpDeviceInfo.size();

	// Device connection, packet size negociation and stream opening
	PvResult lResult = PvResult::Code::NOT_CONNECTED;

    // Connect device
	lResult = pDeviceInfo->mDevice.Connect( aDI, PvAccessControl );
    if ( !lResult.IsOK() )
    {
		Disconnect(pDeviceInfo);
        return FALSE;
    }

    // Perform automatic packet size negociation
    lResult = pDeviceInfo->mDevice.NegotiatePacketSize( 0, 1440); //1440
    if ( !lResult.IsOK() )
    {
        ::Sleep( 2500 );
    }

    // Open stream - and retry if it fails
	for ( ;; )
	{
        // Open stream
        lResult = pDeviceInfo->mStream.Open( aDI->GetIPAddress() );
		if ( lResult.IsOK() )
		{
			break;
		}

		::Sleep( 1000 );
	}

    // Now that the stream is opened, set the destination on the device
    pDeviceInfo->mDevice.SetStreamDestination( pDeviceInfo->mStream.GetLocalIPAddress(), pDeviceInfo->mStream.GetLocalPort() );

	if ( !lResult.IsOK() )
	{
		Disconnect(pDeviceInfo);

		return FALSE;
	}

    // Register to all events of the parameters in the device's node map
    PvGenParameterArray *lGenDevice = pDeviceInfo->mDevice.GetGenParameters();
    for ( PvUInt32 i = 0; i < lGenDevice->GetCount(); i++ )
    {
	    lGenDevice->Get( i )->RegisterEventSink( pDeviceInfo );
    }

	PvGenParameterArray *lDeviceParams = pDeviceInfo->mDevice.GetGenLink();
	PvGenBoolean *mLinkRecoveryEnabled = dynamic_cast<PvGenBoolean *>( lDeviceParams->Get( "LinkRecoveryEnabled" ) );
    mLinkRecoveryEnabled->SetValue( true );


	pDeviceInfo->mIPAddress = aDI->GetIPAddress();
	pDeviceInfo->mMACAddress = aDI->GetMACAddress();
	pDeviceInfo->mModelName = aDI->GetModel();

	PvGenCommand *lStart = dynamic_cast<PvGenCommand *>( pDeviceInfo->mDevice.GetGenParameters()->Get( "AcquisitionStart" ) );
	ASSERT( lStart != NULL ); // Mandatory parameter

	PvGenCommand *lStop = dynamic_cast<PvGenCommand *>( pDeviceInfo->mDevice.GetGenParameters()->Get( "AcquisitionStop" ) );
	ASSERT( lStop != NULL ); // Mandatory parameter

    mAcquiringImages = false;

	// Ready image reception
	StartStreaming(pDeviceInfo);

	// Sync up UI
	//EnableInterface();

	return TRUE;
}

// =============================================================================
void CStGEMultiCameraDlg::OnDestroy()
{
	CDialog::OnDestroy();

	while(mpDeviceInfo.size()>0){
		Disconnect(mpDeviceInfo[0]);
	};


}

// =============================================================================
void CStGEMultiCameraDlg::Disconnect(CDeviceInfo *pDeviceInfo)
{

    // Unregister all events of the parameters in the device's node map
    PvGenParameterArray *lGenDevice = pDeviceInfo->mDevice.GetGenParameters();
    for ( PvUInt32 i = 0; i < lGenDevice->GetCount(); i++ )
    {
	    lGenDevice->Get( i )->UnregisterEventSink( pDeviceInfo );
    }

	// If streaming, stop streaming
	StopStreaming(pDeviceInfo);

	pDeviceInfo->mDevice.Disconnect();
    
	pDeviceInfo->mStream.Close();

	delete pDeviceInfo;
	std::vector<CDeviceInfo*>::iterator it1 = mpDeviceInfo.begin();
    for ( PvUInt32 i = 0; i < mpDeviceInfo.size(); i++ )
	{
		if( *it1==pDeviceInfo ){
			mpDeviceInfo.erase(it1);
			break;
		}
		std::advance( it1, 1 );
	}
	
}

// =============================================================================
void CStGEMultiCameraDlg::StartStreaming(CDeviceInfo *pDeviceInfo)
{

	// Create display window
	CString szTitle;
	CString szModelName;
	CString szMACAddress;

	pDeviceInfo->mPreview = new CPreview;
	pDeviceInfo->mPreview->Create(IDD_DIALOG_PREVIEW,CWnd::GetDesktopWindow());
	szModelName = pDeviceInfo->mModelName.GetUnicode();
	szMACAddress = pDeviceInfo->mMACAddress.GetUnicode();
	szTitle.Format( _T("Preview - %s(%s)"), szModelName, szMACAddress);
	pDeviceInfo->mPreview->SetWindowText(szTitle);
	//pDeviceInfo->mPreview->ShowWindow(SW_SHOW);
	pDeviceInfo->mPreview->SetWindowPos(
							NULL,
							0+(pDeviceInfo->mID-1)*40,
							0+(pDeviceInfo->mID-1)*40,
							0,0,SWP_NOZORDER | SWP_NOSIZE);
	RECT aRect;
	pDeviceInfo->mPreview->GetClientRect(&aRect);

	pDeviceInfo->mPreview->mDisplay.Create( pDeviceInfo->mPreview->GetSafeHwnd(), 10000+pDeviceInfo->mID ); 
	pDeviceInfo->mPreview->mDisplay.SetPosition( 0, 0, aRect.right-aRect.left, aRect.bottom-aRect.top );
	pDeviceInfo->mPreview->mDisplay.SetBackgroundColor( 0xA0, 0xA0, 0xA0 );

	// Create display thread
	pDeviceInfo->mThreadDisplay = new Thread( &pDeviceInfo->mPreview->mDisplay, &pDeviceInfo->mDevice, &pDeviceInfo->mPipeline );

	// Start threads
	pDeviceInfo->mThreadDisplay->Start();
	pDeviceInfo->mThreadDisplay->SetPriority( THREAD_PRIORITY_ABOVE_NORMAL );

    // Start pipeline
    pDeviceInfo->mPipeline.Start();

}


// =============================================================================
void CStGEMultiCameraDlg::StopStreaming(CDeviceInfo *pDeviceInfo)
{

    // Stop display thread
	if ( pDeviceInfo->mThreadDisplay != NULL )
	{
		pDeviceInfo->mThreadDisplay->Stop();

		delete pDeviceInfo->mThreadDisplay;
		pDeviceInfo->mThreadDisplay = NULL;
	}

	// Stop stream thread
    if ( pDeviceInfo->mPipeline.IsStarted() )
    {
		pDeviceInfo->mPipeline.Stop();
    }

	if( pDeviceInfo->mPreview )
	{
		pDeviceInfo->mPreview->DestroyWindow();

		delete pDeviceInfo->mPreview;
		pDeviceInfo->mPreview = NULL;
	}
}

// =============================================================================
void CStGEMultiCameraDlg::SetCameraTree()
{
	HTREEITEM hItem, hChildItem, hFirstItem=NULL;
	CString strTmp;
	mTreeConnectDevice.DeleteAllItems();
	CString szModelName;
	CString szMACAddress;
	CString szIPAddress;
	for( unsigned int z = 0; z < mpDeviceInfo.size(); z++ ){
		szModelName= mpDeviceInfo[z]->mModelName.GetUnicode();
		szMACAddress = mpDeviceInfo[z]->mMACAddress.GetUnicode();

		strTmp.Format(_T("%s(%s)"), szModelName, szMACAddress );
		hChildItem = mTreeConnectDevice.InsertItem(strTmp, TVI_ROOT);
		mTreeConnectDevice.SetItemData( hChildItem, z );

		szIPAddress = mpDeviceInfo[z]->mIPAddress.GetUnicode();
		strTmp.Format(_T("IP Address(%s)"),szIPAddress );
		hItem = mTreeConnectDevice.InsertItem(strTmp, hChildItem);
		mTreeConnectDevice.SetItemData( hItem, z );
	}
}

// =============================================================================
void CStGEMultiCameraDlg::StartAcquisition(CDeviceInfo *pDeviceInfo)
{
	PvGenEnum *lMode = dynamic_cast<PvGenEnum *>( pDeviceInfo->mDevice.GetGenParameters()->Get( "AcquisitionMode" ) );
	PvGenCommand *lStart = dynamic_cast<PvGenCommand *>( pDeviceInfo->mDevice.GetGenParameters()->Get( "AcquisitionStart" ) );
	PvGenInteger *lTLParamsLocked = dynamic_cast<PvGenInteger *>( pDeviceInfo->mDevice.GetGenParameters()->Get( "TLParamsLocked" ) );
	PvGenInteger *lPayloadSize = dynamic_cast<PvGenInteger *>( pDeviceInfo->mDevice.GetGenParameters()->Get( "PayloadSize" ) );
	PvGenCommand *lResetStats = dynamic_cast<PvGenCommand *>( pDeviceInfo->mStream.GetParameters()->Get( "Reset" ) );

    // Try reading payload size from device
    PvInt64 lPayloadSizeValue = 0;
    if ( lPayloadSize != NULL )
    {
        lPayloadSize->GetValue( lPayloadSizeValue );
    }

    // If payload size is valid, force buffers re-alloc - better than 
    // adjusting as images are comming in
    if ( lPayloadSizeValue > 0 )
    {
        pDeviceInfo->mPipeline.SetBufferSize( static_cast<PvUInt32>( lPayloadSizeValue ) );
    }

    // Never hurts to start streaming on a fresh pipeline/stream...
    pDeviceInfo->mPipeline.Reset();

    // Reset stream statistics
    lResetStats->Execute();

	PvResult lResult = PvResult::Code::NOT_INITIALIZED;

	PvString lStr;
	lMode->GetValue( lStr );
	CString lModeStr;
	lModeStr = lStr.GetUnicode();
	if ( lModeStr.Find( _T( "Continuous" ) ) >= 0 )
	{
		// We are streaming, lock the TL parameters
		if ( lTLParamsLocked != NULL ) 
		{
			lResult = lTLParamsLocked->SetValue( 1 );
		}

		lStart->Execute();
	}
	else if ( ( lModeStr.Find( _T( "Multi" ) ) >= 0 ) || 
			  ( lModeStr.Find( _T( "Single" ) ) >= 0 ) )
	{
		// We are streaming, lock the TL parameters
		if ( lTLParamsLocked != NULL ) 
		{
			lTLParamsLocked->SetValue( 1 );
		}

		lResult = lStart->Execute();

		// We are done streaming, unlock the TL parameters
		if ( lTLParamsLocked != NULL ) 
		{
			lTLParamsLocked->SetValue( 0 );
		}
	}

}


// =============================================================================
void CStGEMultiCameraDlg::StopAcquisition(CDeviceInfo *pDeviceInfo)
{
	if( pDeviceInfo->mDevice.IsConnected() ){
		PvGenCommand *lStop = dynamic_cast<PvGenCommand *>( pDeviceInfo->mDevice.GetGenParameters()->Get( "AcquisitionStop" ) );
		ASSERT( lStop != NULL ); // Mandatory parameter

		PvResult lResult = lStop->Execute();

		// TLParamsLocked - Optionnal
		PvGenInteger *lTLParamsLocked = dynamic_cast<PvGenInteger *>( pDeviceInfo->mDevice.GetGenParameters()->Get( "TLParamsLocked" ) );
		if ( lTLParamsLocked != NULL )
		{
			lResult = lTLParamsLocked->SetValue( 0 );
		}
	}
}

// =============================================================================
void CStGEMultiCameraDlg::OnTvnSelchangedTreeConnectdevice(NMHDR *pNMHDR, LRESULT *pResult)
{
	LPNMTREEVIEW pNMTreeView = reinterpret_cast<LPNMTREEVIEW>(pNMHDR);

	HTREEITEM hItem = pNMTreeView->itemNew.hItem;
	if( hItem ){
		int iData = (int)mTreeConnectDevice.GetItemData(hItem);
		//mpDeviceInfo[iData]->mPreview->ShowWindow(SW_SHOW);
	}

	*pResult = 0;
}

// =============================================================================
void CStGEMultiCameraDlg::EnableInterface()
{
	// This method can be called really early or late when the window is not created
	if ( GetSafeHwnd() == 0 )
	{
		return;
	}
	bool bStart = false;
	bool bStop = false;

	if( mpDeviceInfo.size()>0 ){
		if( IsAcquiringImages() ){
			bStop = true;
		}
		else
		{
			bStart = true;
		}
	}
	GetDlgItem( IDC_BUTTON_START )->EnableWindow( bStart );
	GetDlgItem( IDC_BUTTON_STOP )->EnableWindow( bStop );

}