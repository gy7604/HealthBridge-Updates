import base64
import copy
import hashlib
import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch
import healthbridge_publish as sp


class PublisherTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
        self.now=1793664000
        self.apk=b'APK bytes used only with the synthetic verifier'
        self.digest=hashlib.sha256(self.apk).hexdigest()
        self.receipt=dict(schema=1,appId='healthbridge',requestId='build-1',snapshotSha='a'*40,mode='build',
            compiled=True,checksPassed=True,signed=True,apkBuilt=True,installed=False,publication='NOT_APPROVED',
            package=sp.PACKAGE,versionCode=4,versionName='0.1.3',certificateSha256=sp.CERT,
            signer='ORIGINAL_OWNER_ENROLLED_KEY',artifacts=[dict(name='candidate.apk',bytes=len(self.apk),sha256=self.digest)])
        self.bundle(self.receipt)
        self.event=dict(action='created',repository=dict(full_name=sp.REPO),sender=dict(login='gy7604'),
            issue=dict(number=42,title='HEALTHBRIDGE-PUBLICATION-CONTROL-v1',user=dict(login='gy7604')),
            comment=dict(id=123,user=dict(login='gy7604'),created_at='2026-11-03T00:00:00Z',updated_at='2026-11-03T00:00:00Z'))
        self.refresh_request()
        self.baseline=dict(packageName=sp.PACKAGE,signingCertSha256=sp.CERT,versionCode=3,
            versionName='0.1.2',sha256='f'*64,sizeBytes=1000,
            apkUrl=f'https://github.com/{sp.REPO}/releases/download/v0.1.2/HealthBridge-0.1.2.apk')
        self.release=None; self.saved=None; self.calls=[]; self.bad_digest=False; self.existing=False; self.bootstrap=False
    def tearDown(self): self.temp.cleanup()
    def bundle(self,receipt,extras=None):
        with zipfile.ZipFile(self.root/'approved.zip','w') as z:
            z.writestr('candidate.apk',self.apk); z.writestr('receipt.json',json.dumps(receipt))
            for name,data in (extras or {}).items(): z.writestr(name,data)
    def refresh_request(self):
        self.outer=hashlib.sha256((self.root/'approved.zip').read_bytes()).hexdigest()
        self.event['comment']['body']=f'/healthbridge-publish approve build-1 {"a"*40} 4 {self.digest} {"c"*40} {self.outer} sealed-v1\n\n승인한 변경 내용'
        self.request=sp.validate_event(self.event,self.now,42)
    def verify(self,path):
        self.assertEqual(path.read_bytes(),self.apk)
        return {k:self.receipt[k] for k in ('package','versionCode','versionName','certificateSha256')}
    def read(self,path,method='GET',body=None):
        self.calls.append((method,path,copy.deepcopy(body)))
        prefix=sp.PREFIX
        if path==prefix: return dict(full_name=sp.REPO,private=False,archived=False,default_branch='main')
        if '/issues/comments/' in path:
            return self.event['comment'] | {'issue_url':f'https://api.github.com/repos/{sp.REPO}/issues/42'}
        if path==prefix+'/contents?ref=main':
            return [{'name':'latest.json'}] if self.saved is not None or not self.bootstrap else [{'name':'README.md'}]
        if path==prefix+'/contents/latest.json?ref=main':
            data=self.saved if self.saved is not None else self.baseline
            return dict(sha='d'*40 if self.saved is not None else 'c'*40,encoding='base64',size=100,
                        content=base64.b64encode(json.dumps(data).encode()).decode())
        if '/git/matching-refs/' in path: return []
        if '/releases?' in path:
            if self.existing:return [{'id':20,'tag_name':'v0.1.3'}]
            if self.bootstrap and self.release is not None:return [copy.deepcopy(self.release)]
            return []
        if path==prefix+'/releases/latest':
            if self.release is not None and self.release['draft'] is False:return copy.deepcopy(self.release)
            return dict(id=8,tag_name='v0.1.2',draft=False,prerelease=False,
                assets=[dict(browser_download_url=self.baseline['apkUrl'],size=1000,digest='sha256:'+'f'*64)])
        if path.endswith('/git/ref/heads/main'): return dict(object=dict(sha='e'*40))
        if path==prefix+'/releases' and method=='POST':
            self.release=body | dict(id=9,assets=[]); return copy.deepcopy(self.release)
        if path==prefix+'/releases/9':
            if method=='PATCH': self.release.update(body)
            return copy.deepcopy(self.release)
        if path==prefix+'/contents/latest.json' and method=='PUT':
            if self.bootstrap:self.assertNotIn('sha',body)
            else:self.assertEqual(body['sha'],'c'*40)
            self.saved=json.loads(base64.b64decode(body['content'])); return {'content':{'sha':'d'*40}}
        raise AssertionError('Unexpected endpoint '+path)
    def upload(self,args):
        self.assertEqual(args[0:3],['release','upload','v0.1.3'])
        self.assertEqual(args[-2:],['--repo',sp.REPO])
        self.assertEqual(Path(args[3]).read_bytes(),self.apk)
        self.release['assets']=[dict(id=10,name='HealthBridge-0.1.3.apk',size=len(self.apk),
            digest='sha256:'+('0'*64 if self.bad_digest else self.digest),
            browser_download_url=f'https://github.com/{sp.REPO}/releases/download/v0.1.3/HealthBridge-0.1.3.apk')]
    def publish(self,**changes):
        args=dict(event=self.event,request=self.request,issue_number=42,root=self.root,
            verify_apk=self.verify,read=self.read,run_gh=self.upload,clock=lambda:self.now)
        args.update(changes); return sp.publish(**args)
    def writes(self): return [c for c in self.calls if c[0]!='GET']
    def test_native_owner_exact_version_baseline_and_notes_are_required(self):
        for part,key,value in [('sender','login','other'),('issue','number',43),
            ('comment','updated_at','edited'),('comment','body',self.event['comment']['body']+'\x00')]:
            e=copy.deepcopy(self.event);e[part][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):sp.validate_event(e,self.now,42)
        for now in (self.now-1,self.now+901):
            with self.assertRaises(ValueError):sp.validate_event(self.event,now,42)
    def test_external_and_redirect_like_download_urls_are_rejected(self):
        for url in ('http://download.oaiusercontent.com/files/x','https://evil.test/files/x',
                    'https://download.oaiusercontent.com.evil.test/files/x',
                    'https://user:pass@download.oaiusercontent.com/files/x',
                    'https://download.oaiusercontent.com/files/x#fragment'):
            with self.subTest(url=url),self.assertRaises(ValueError):sp.file_url(url)
    def test_only_two_bounded_non_secret_files_are_allowed(self):
        for extra in ({'check-log.txt':'private'}, {'../key.pem':'private'}):
            self.bundle(self.receipt,extra); self.refresh_request()
            with self.assertRaises(ValueError):self.publish()
            self.assertEqual(self.writes(),[])
    def test_wrong_signer_source_boolean_schema_or_install_claim_never_writes(self):
        for change in (dict(certificateSha256='f'*64),dict(snapshotSha='b'*40),dict(schema=True),
                       dict(installed=True),dict(publication='PUBLISHED'),dict(package='other')):
            self.bundle(self.receipt | change); self.refresh_request()
            with self.subTest(change=change),self.assertRaises(ValueError):self.publish()
            self.assertEqual(self.writes(),[])
    def test_actual_apk_metadata_must_agree_with_receipt(self):
        with self.assertRaises(ValueError):self.publish(verify_apk=lambda p:self.verify(p)|dict(versionCode=5))
        self.assertEqual(self.writes(),[])
    def test_wrong_bundle_hash_never_extracts_or_writes(self):
        self.request['outerSha256']='0'*64
        with self.assertRaises(ValueError):sp.inspect_bundle(self.root/'approved.zip',self.request,self.root,self.verify)
        self.assertFalse((self.root/'candidate.apk').exists())
    def test_existing_version_or_changed_feed_cannot_be_overwritten(self):
        self.existing=True
        with self.assertRaises(ValueError):self.publish()
        self.assertEqual(self.writes(),[])
    def test_feed_rejects_downgrade_and_wrong_original_signer(self):
        c={k:self.receipt[k] for k in ('versionCode','versionName')}; c.update(sha256=self.digest,sizeBytes=10)
        for baseline in (self.baseline | {'versionCode':4},self.baseline | {'signingCertSha256':'0'*64}):
            with self.assertRaises(ValueError):sp.manifest(c,self.request,baseline)
    def test_verified_prebuilt_apk_updates_only_existing_feed(self):
        result=self.publish()
        self.assertTrue(result['published']);self.assertFalse(result['rebuilt']);self.assertFalse(result['installed'])
        self.assertEqual(self.saved['sha256'],self.digest)
        self.assertEqual(self.saved['notes'],'승인한 변경 내용')
        self.assertEqual([w[0] for w in self.writes()],['POST','PATCH','PUT'])
        self.assertEqual(self.writes()[0][2]['target_commitish'],'e'*40)
    def test_bad_uploaded_digest_leaves_draft_and_does_not_publish_feed(self):
        self.bad_digest=True
        with self.assertRaises(ValueError):self.publish()
        self.assertTrue(self.release['draft']);self.assertIsNone(self.saved)
        self.assertEqual([w[0] for w in self.writes()],['POST'])
    def test_approval_revoked_after_upload_prevents_publication(self):
        read=self.read
        def revoked(path,method='GET',body=None):
            value=read(path,method,body)
            if '/issues/comments/' in path and self.release is not None:return value | {'body':'revoked'}
            return value
        with self.assertRaises(ValueError):self.publish(read=revoked)
        self.assertTrue(self.release['draft']);self.assertIsNone(self.saved)
        self.assertEqual([w[0] for w in self.writes()],['POST'])
    def test_api_guard_never_reaches_protected_app_or_source_endpoints(self):
        for path,method in (('repos/gy7604/worktable/releases','POST'),
                            (sp.PREFIX+'/contents/app/build.gradle.kts','PUT'),
                            ('repos/gy7604/gy7604.github.io/contents/latest.json','PUT')):
            with self.subTest(path=path),self.assertRaises(ValueError):sp.api(path,method,{})
    def test_disagreement_between_feed_and_public_release_stops_before_writes(self):
        read=self.read
        def changed(path,method='GET',body=None):
            value=read(path,method,body)
            return value | {'tag_name':'v0.1.4'} if path.endswith('/releases/latest') else value
        with self.assertRaises(ValueError):self.publish(read=changed)
        self.assertEqual(self.writes(),[])
    def test_feed_change_after_draft_stops_before_publication(self):
        read=self.read
        def changed(path,method='GET',body=None):
            value=read(path,method,body)
            if '/contents/latest.json?' in path and self.release is not None:return value | {'sha':'d'*40}
            return value
        with self.assertRaises(ValueError):self.publish(read=changed)
        self.assertTrue(self.release['draft']);self.assertIsNone(self.saved)
        self.assertEqual([w[0] for w in self.writes()],['POST'])
    def test_unknown_feed_commit_outcome_is_not_reported_as_success(self):
        read=self.read
        def unknown(path,method='GET',body=None):
            if method=='PUT':raise RuntimeError('Unknown commit result')
            return read(path,method,body)
        with self.assertRaises(RuntimeError):self.publish(read=unknown)
        self.assertFalse(self.release['draft']);self.assertIsNone(self.saved)
    def first_publication(self):
        self.bootstrap=True
        self.event['comment']['body']=self.event['comment']['body'].replace('c'*40,'empty')
        self.request=sp.validate_event(self.event,self.now,42)
    def test_first_publication_creates_feed_only_after_exact_empty_approval(self):
        self.first_publication()
        result=self.publish()
        self.assertTrue(result['published']);self.assertEqual(self.saved['versionCode'],4)
        self.assertNotIn('sha',self.writes()[-1][2])
    def test_empty_approval_rejects_an_existing_feed_before_any_write(self):
        self.first_publication();self.saved=self.baseline
        with self.assertRaises(ValueError):self.publish()
        self.assertEqual(self.writes(),[])
    def test_first_publication_cannot_reuse_an_existing_draft(self):
        self.first_publication();self.existing=True
        with self.assertRaises(ValueError):self.publish()
        self.assertEqual(self.writes(),[])
    def test_race_creating_feed_after_draft_prevents_publishing(self):
        self.first_publication();read=self.read
        def changed(path,method='GET',body=None):
            value=read(path,method,body)
            if path.endswith('/contents?ref=main') and self.release is not None:return [{'name':'latest.json'}]
            return value
        with self.assertRaises(ValueError):self.publish(read=changed)
        self.assertTrue(self.release['draft']);self.assertIsNone(self.saved)
    def test_missing_feed_cannot_be_treated_as_empty_without_explicit_approval(self):
        candidate=dict(versionCode=4,versionName='0.1.3',sha256=self.digest,sizeBytes=100)
        with self.assertRaises(ValueError):sp.manifest(candidate,self.request,None)
    def test_other_apps_activation_and_control_issue_cannot_enable_this_publisher(self):
        e=copy.deepcopy(self.event);e['issue']['title']='SANGIL-PUBLICATION-CONTROL-v1'
        with self.assertRaises(ValueError):sp.validate_event(e,self.now,42)
        env=dict(GITHUB_REPOSITORY=sp.REPO,GITHUB_ACTOR='gy7604',GITHUB_EVENT_NAME='issue_comment',
                 GITHUB_RUN_ATTEMPT='1',SANGIL_PUBLICATION_ENABLED='true')
        with patch.dict(os.environ,env,clear=True),patch.object(sys,'argv',['publisher','--event','not-created.json']):
            with self.assertRaisesRegex(ValueError,'Separately enabled'):sp.main()


    def test_public_approval_never_accepts_a_plain_private_file_reference(self):
        private='https://synthetic.oaiusercontent.com/files/fixture-only'
        for body in (self.event['comment']['body'].replace('sealed-v1',private),
                     self.event['comment']['body']+'\n'+private):
            event=copy.deepcopy(self.event);event['comment']['body']=body
            with self.assertRaises(ValueError):sp.validate_event(event,self.now,42)

    def test_file_reference_is_received_only_through_bounded_private_pipe(self):
        private='https://synthetic.oaiusercontent.com/files/fixture-only'
        result=Mock(returncode=0,stdout=json.dumps({'url':private}),stderr='')
        event=copy.deepcopy(self.event);event['issue']['number']=1
        with patch.object(sp.subprocess,'run',return_value=result) as run:
            self.assertEqual(sp.receive_file_url(event,self.request,1),private)
        args,kwargs=run.call_args
        self.assertEqual(args[0][0],'node')
        self.assertEqual(args[0][-1],'--receive-private-pipe')
        self.assertNotIn(private,json.dumps(args))
        payload=json.loads(kwargs['input'])
        self.assertEqual(payload['appId'],'healthbridge')
        self.assertEqual(payload['requestId'],self.request['requestId'])
        self.assertTrue(kwargs['capture_output'])
        self.assertEqual(kwargs['timeout'],205)

    def test_failed_or_malformed_private_transfer_never_calls_publication(self):
        for result in (Mock(returncode=1,stdout='',stderr='synthetic-secret'),
                       Mock(returncode=0,stdout='x'*13001,stderr=''),
                       Mock(returncode=0,stdout=json.dumps({'url':'https://evil.invalid/files/x'}),stderr=''),
                       Mock(returncode=0,stdout=json.dumps({'url':'https://synthetic.oaiusercontent.com/files/x','extra':True}),stderr='')):
            with self.subTest(result=result),patch.object(sp.subprocess,'run',return_value=result),self.assertRaises(ValueError):
                sp.receive_file_url(self.event,self.request,1)
        self.assertEqual(self.writes(),[])

    def test_private_transfer_cannot_use_another_control_issue(self):
        with patch.object(sp.subprocess,'run') as run:
            with self.assertRaises(ValueError):sp.receive_file_url(self.event,self.request,42)
            run.assert_not_called()


if __name__=='__main__':unittest.main()
