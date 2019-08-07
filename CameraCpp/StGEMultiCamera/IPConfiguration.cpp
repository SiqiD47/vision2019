// *****************************************************************************
//
//
//
// *****************************************************************************
// IPConfiguration.cpp : 
//

#include "stdafx.h"
#include "StGEMultiCamera.h"
#include "IPConfiguration.h"


// CIPConfiguration dialog

IMPLEMENT_DYNAMIC(CIPConfiguration, CDialog)

CIPConfiguration::CIPConfiguration(CWnd* pParent /*=NULL*/)
	: CDialog(CIPConfiguration::IDD, pParent)
{
	m_iDeviceCount = 0;
	hCurrentItem = NULL;
}

CIPConfiguration::~CIPConfiguration()
{
}

void CIPConfiguration::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	DDX_Control(pDX, IDC_TREE_DEVICE, mTreeDevice);
	DDX_Control(pDX, IDC_IPADDRESS_CURRENTIPADDRESS, m_ipCurrentIPAddress);
	DDX_Control(pDX, IDC_IPADDRESS_CURRENTSUBNETMASK, m_ipCurrentSubnetmask);
	DDX_Control(pDX, IDC_IPADDRESS_CURRENTDEFAULTGATEWAY, m_ipCurrentDefaultgateway);
	DDX_Control(pDX, IDC_IPADDRESS_NEWIPADDRESS, m_ipNewIPAddress);
	DDX_Control(pDX, IDC_IPADDRESS_NEWSUBNETMASK, m_ipNewSubnetmask);
	DDX_Control(pDX, IDC_IPADDRESS_NEWDEFAULTGATEWAY, m_ipNewDefaultgateway);
}


BEGIN_MESSAGE_MAP(CIPConfiguration, CDialog)
	ON_BN_CLICKED(IDOK, &CIPConfiguration::OnBnClickedOk)
	ON_BN_CLICKED(IDCANCEL, &CIPConfiguration::OnBnClickedCancel)
	ON_BN_CLICKED(IDC_BUTTON_UP, &CIPConfiguration::OnBnClickedButtonUp)
	ON_WM_TIMER()
	ON_NOTIFY(NM_CLICK, IDC_TREE_DEVICE, &CIPConfiguration::OnNMClickTreeDevice)
	ON_NOTIFY(TVN_SELCHANGED, IDC_TREE_DEVICE, &CIPConfiguration::OnTvnSelchangedTreeDevice)
	ON_BN_CLICKED(IDC_BUTTON_APPLY, &CIPConfiguration::OnBnClickedButtonApply)
END_MESSAGE_MAP()


// CIPConfiguration

void CIPConfiguration::OnBnClickedOk()
{
	OnOK();
}

void CIPConfiguration::OnBnClickedCancel()
{
	OnCancel();
}

void CIPConfiguration::OnBnClickedButtonUp()
{
	SearchCamera(1000);
	SetCameraTree();
	SetCurrentInfomation();

}

void CIPConfiguration::SearchCamera( INT iTimeout )
{
	S_CAMERA_CONFIGURATION tmpConfig;


	PvResult pvResult;
	PvDeviceInfo *lDeviceInfo = NULL;
	m_iDeviceCount=0;

	mlSystem.SetDetectionTimeout( iTimeout );
	pvResult = mlSystem.Find();
	mCameraConfig.clear();
	if( pvResult.IsOK() )
	{
		PvUInt32 lInterfaceCount = mlSystem.GetInterfaceCount();

		for( PvUInt32 x = 0; x < lInterfaceCount; x++ )
		{
			// get pointer to each of interface
			PvInterface * lInterface = mlSystem.GetInterface( x );

			// Get the number of GEV devices that were found using GetDeviceCount.
			PvUInt32 lDeviceCount = lInterface->GetDeviceCount();

			for( PvUInt32 y = 0; y < lDeviceCount ; y++ )
			{
				lDeviceInfo = lInterface->GetDeviceInfo( y );
				BOOL bAdd = TRUE;
				CString szMACAddress;
				szMACAddress = lDeviceInfo->GetMACAddress().GetUnicode();
				for( unsigned int z = 0; z < mCameraConfig.size(); z++ ){
					if( szMACAddress.Compare(mCameraConfig[z].szMACAddress)==0 ){
						bAdd = FALSE;
						break;
					}
				}
				if( bAdd ){
					m_iDeviceCount++;
					tmpConfig.szMACAddress = szMACAddress;
					tmpConfig.szIPAddress = lDeviceInfo->GetIPAddress().GetUnicode();
					tmpConfig.szSubnetMask = lDeviceInfo->GetSubnetMask().GetUnicode();
					tmpConfig.szDefaultGateway = lDeviceInfo->GetDefaultGateway().GetUnicode();
					tmpConfig.szModelName = lDeviceInfo->GetModel().GetUnicode();
					mCameraConfig.push_back(tmpConfig);
				}
			}
		}
	}
}


void CIPConfiguration::SetCameraTree()
{
	HTREEITEM hItem, hChildItem, hFirstItem=NULL;
	CString strTmp;
	mTreeDevice.DeleteAllItems();
	for( unsigned int z = 0; z < mCameraConfig.size(); z++ ){
		strTmp.Format("%s(%s)",mCameraConfig[z].szModelName, mCameraConfig[z].szMACAddress );
		hChildItem = mTreeDevice.InsertItem(strTmp, TVI_ROOT);
		mTreeDevice.SetItemData( hChildItem, z );
		if( z==0 )	hFirstItem=hChildItem;

		strTmp.Format("IP Address(%s)",mCameraConfig[z].szIPAddress );
		hItem = mTreeDevice.InsertItem(strTmp, hChildItem);
		mTreeDevice.SetItemData( hItem, z );
		strTmp.Format("SubnetMask(%s)",mCameraConfig[z].szSubnetMask );
		hItem = mTreeDevice.InsertItem(strTmp, hChildItem);
		mTreeDevice.SetItemData( hItem, z );
		strTmp.Format("Default gateway(%s)",mCameraConfig[z].szDefaultGateway );
		hItem = mTreeDevice.InsertItem(strTmp, hChildItem);
		mTreeDevice.SetItemData( hItem, z );
	}
	if( hFirstItem ){
		mTreeDevice.SelectItem(hFirstItem);
	}
	hCurrentItem = hFirstItem;
}

void GetDataFromAddress( PBYTE pbyteData, CString szText )
{
	int iX = szText.Find(".",0);
	pbyteData[0] = (BYTE)_tstoi(szText.Left(iX));
	szText = szText.Mid(iX+1);
	iX = szText.Find(".",0);
	pbyteData[1] = (BYTE)_tstoi(szText.Left(iX));
	szText = szText.Mid(iX+1);
	iX = szText.Find(".",0);
	pbyteData[2] = (BYTE)_tstoi(szText.Left(iX));
	szText = szText.Mid(iX+1);
	pbyteData[3] = (BYTE)_tstoi(szText);
}

void CIPConfiguration::SetCurrentInfomation()
{
	HTREEITEM hItem = mTreeDevice.GetSelectedItem();
	BYTE byteIPAddress[4];
	BYTE byteSubnetmask[4];
	BYTE bytedefaultGateway[4];
	memset( byteIPAddress,0,sizeof(byteIPAddress) );
	memset( byteSubnetmask,0,sizeof(byteSubnetmask) );
	memset( bytedefaultGateway,0,sizeof(bytedefaultGateway) );
	if( hItem ){
		int iData = (int)mTreeDevice.GetItemData(hItem);
		GetDataFromAddress( byteIPAddress, mCameraConfig[iData].szIPAddress );
		GetDataFromAddress( byteSubnetmask, mCameraConfig[iData].szSubnetMask );
		GetDataFromAddress( bytedefaultGateway, mCameraConfig[iData].szDefaultGateway );
	}

	m_ipCurrentIPAddress.SetAddress(byteIPAddress[0],byteIPAddress[1],byteIPAddress[2],byteIPAddress[3]);
	m_ipCurrentSubnetmask.SetAddress(byteSubnetmask[0],byteSubnetmask[1],byteSubnetmask[2],byteSubnetmask[3]);
	m_ipCurrentDefaultgateway.SetAddress(bytedefaultGateway[0],bytedefaultGateway[1],bytedefaultGateway[2],bytedefaultGateway[3]);

	m_ipNewIPAddress.SetAddress(byteIPAddress[0],byteIPAddress[1],byteIPAddress[2],byteIPAddress[3]);
	m_ipNewSubnetmask.SetAddress(byteSubnetmask[0],byteSubnetmask[1],byteSubnetmask[2],byteSubnetmask[3]);
	m_ipNewDefaultgateway.SetAddress(bytedefaultGateway[0],bytedefaultGateway[1],bytedefaultGateway[2],bytedefaultGateway[3]);

}
void CIPConfiguration::OnTimer(UINT_PTR nIDEvent)
{
	if( nIDEvent==1 ){
		SearchCamera(10);
		SetCameraTree();
		SetCurrentInfomation();
		KillTimer( nIDEvent );
	}
	CDialog::OnTimer(nIDEvent);
}

BOOL CIPConfiguration::OnInitDialog()
{
	CDialog::OnInitDialog();

	SetTimer( 1, 10, NULL );

	return TRUE;
}

void CIPConfiguration::OnNMClickTreeDevice(NMHDR *pNMHDR, LRESULT *pResult)
{

	*pResult = 0;
}

void CIPConfiguration::OnTvnSelchangedTreeDevice(NMHDR *pNMHDR, LRESULT *pResult)
{
	LPNMTREEVIEW pNMTreeView = reinterpret_cast<LPNMTREEVIEW>(pNMHDR);

	SetCurrentInfomation();

	*pResult = 0;
}

void CIPConfiguration::OnBnClickedButtonApply()
{

	HTREEITEM hItem = mTreeDevice.GetSelectedItem();
	if( hItem ){
		int iData = (int)mTreeDevice.GetItemData(hItem);
		PvString pvMACAddress(mCameraConfig[iData].szMACAddress);
		CString lIPAddress, lSubnetmask, lDefaultGateway;
		BYTE byteIPAddress[4];
		BYTE byteSubnetmask[4];
		BYTE byteDefaultgateway[4];
		m_ipNewIPAddress.GetAddress(byteIPAddress[0],byteIPAddress[1],byteIPAddress[2],byteIPAddress[3]);
		lIPAddress.Format(_T("%d.%d.%d.%d"),byteIPAddress[0],byteIPAddress[1],byteIPAddress[2],byteIPAddress[3]);
		m_ipNewSubnetmask.GetAddress(byteSubnetmask[0],byteSubnetmask[1],byteSubnetmask[2],byteSubnetmask[3]);
		lSubnetmask.Format(_T("%d.%d.%d.%d"),byteSubnetmask[0],byteSubnetmask[1],byteSubnetmask[2],byteSubnetmask[3]);
		m_ipNewDefaultgateway.GetAddress(byteDefaultgateway[0],byteDefaultgateway[1],byteDefaultgateway[2],byteDefaultgateway[3]);
		lDefaultGateway.Format(_T("%d.%d.%d.%d"),byteDefaultgateway[0],byteDefaultgateway[1],byteDefaultgateway[2],byteDefaultgateway[3]);
		PvString pvIPAddress(lIPAddress);
		PvString pvSubnetmask(lSubnetmask);
		PvString pvDefaultGateway(lDefaultGateway);

		PvResult lResult = PvDevice::SetIPConfiguration(pvMACAddress,pvIPAddress ,pvSubnetmask ,pvDefaultGateway );

		if( lResult.IsOK() ){
			m_ipCurrentIPAddress.SetAddress(byteIPAddress[0],byteIPAddress[1],byteIPAddress[2],byteIPAddress[3]);
			m_ipCurrentSubnetmask.SetAddress(byteSubnetmask[0],byteSubnetmask[1],byteSubnetmask[2],byteSubnetmask[3]);
			m_ipCurrentDefaultgateway.SetAddress(byteDefaultgateway[0],byteDefaultgateway[1],byteDefaultgateway[2],byteDefaultgateway[3]);
			mCameraConfig[iData].szIPAddress=lIPAddress;
			mCameraConfig[iData].szSubnetMask=lSubnetmask;
			mCameraConfig[iData].szDefaultGateway=lDefaultGateway;
			CameraTreeApply(byteIPAddress, byteSubnetmask, byteDefaultgateway );
		}
		else	//Error
		{
			AfxMessageBox( _T("Error Change IP Configuration!") );
		}
	}

}

void CIPConfiguration::CameraTreeApply(PBYTE pbyteIPAddress, PBYTE pbyteSubnetmask, PBYTE pbyteDefaultgateway )
{
	HTREEITEM hTmpItem;
	HTREEITEM hItem = mTreeDevice.GetSelectedItem();
	if( hItem==NULL ) return;
	do{
		hTmpItem = mTreeDevice.GetParentItem(hItem);
		if( hTmpItem==TVI_ROOT || hTmpItem==NULL ) break;
		hItem = hTmpItem;
	}while(1);

	CString szText, strTmp;
	hTmpItem = mTreeDevice.GetChildItem(hItem);
	while(hTmpItem){
		szText = mTreeDevice.GetItemText(hTmpItem);
		if( szText.Find(_T("IP Address"))==0 ){
			strTmp.Format("IP Address(%d.%d.%d.%d)",pbyteIPAddress[0],pbyteIPAddress[1],pbyteIPAddress[2],pbyteIPAddress[3] );
			mTreeDevice.SetItemText(hTmpItem,strTmp);
		}
		else if( szText.Find(_T("SubnetMask"))==0 ){
			strTmp.Format("SubnetMask(%d.%d.%d.%d)",pbyteSubnetmask[0],pbyteSubnetmask[1],pbyteSubnetmask[2],pbyteSubnetmask[3] );
			mTreeDevice.SetItemText(hTmpItem,strTmp);
		}
		else if( szText.Find(_T("Default gateway"))==0 ){
			strTmp.Format("Default gateway(%d.%d.%d.%d)",pbyteDefaultgateway[0],pbyteDefaultgateway[1],pbyteDefaultgateway[2],pbyteDefaultgateway[3] );
			mTreeDevice.SetItemText(hTmpItem,strTmp);
		}
		hTmpItem = mTreeDevice.GetNextItem(hTmpItem, TVGN_NEXT);

	};

}